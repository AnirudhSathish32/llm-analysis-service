import os
import logging
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
import google.generativeai as genai

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("RAG_TOP_K", "4"))
EMBEDDING_MODEL = "models/embedding-001"


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

def _embed(texts: list[str]) -> list[list[float]]:
    """Call Google's embedding API for a batch of texts."""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts,
        task_type="retrieval_document",
    )
    return result["embedding"] if isinstance(texts, str) else result["embedding"]


def _embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]


# ---------------------------------------------------------------------------
# ChromaDB client
# ---------------------------------------------------------------------------

def _get_chroma_collection(document_id: str) -> chromadb.Collection:
    """
    Each document gets its own ChromaDB collection.
    Collection name = document_id so retrieval is always scoped to one doc.
    """
    client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    # get_or_create so ingestion and retrieval both work without extra checks
    return client.get_or_create_collection(name=f"doc_{document_id}")


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def _load_file(file_path: str) -> list:
    """
    Use the appropriate LangChain loader based on file extension.
    Returns a list of LangChain Document objects.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    elif ext == ".csv":
        loader = CSVLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf, .txt, .csv")

    return loader.load()


# ---------------------------------------------------------------------------
# Phase 1 — Ingestion
# ---------------------------------------------------------------------------

async def ingest_document(file_path: str, document_id: str) -> int:
    """
    Load a file, chunk it, embed the chunks, store in ChromaDB.
    Returns the number of chunks stored.

    Called once when a document is uploaded.
    """
    logger.info("Ingesting document %s from %s", document_id, file_path)

    # 1. Load raw text via LangChain
    raw_docs = _load_file(file_path)

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(raw_docs)

    if not chunks:
        raise ValueError("Document produced no chunks after splitting — file may be empty.")

    # 3. Extract text and metadata from each chunk
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [
        {
            "document_id": document_id,
            "source": chunk.metadata.get("source", file_path),
            # PDFs carry page numbers; other loaders may not
            "page": str(chunk.metadata.get("page", "unknown")),
        }
        for chunk in chunks
    ]
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]

    # 4. Embed all chunks in one batch call
    embeddings = _embed(texts)

    # 5. Store in ChromaDB
    collection = _get_chroma_collection(document_id)
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    logger.info("Stored %d chunks for document %s", len(chunks), document_id)
    return len(chunks)


# ---------------------------------------------------------------------------
# Phase 2 — Retrieval
# ---------------------------------------------------------------------------

async def retrieve_chunks(document_id: str, query: str) -> list[dict]:
    """
    Embed the query, find the top-K closest chunks in ChromaDB.
    Returns a list of dicts with 'text', 'page', and 'source' keys.

    Called on every user query before hitting the LLM.
    """
    logger.info("Retrieving chunks for document %s, query: %.60s...", document_id, query)

    query_embedding = _embed_query(query)
    collection = _get_chroma_collection(document_id)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas"],
    )

    chunks = []
    for text, metadata in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({
            "text": text,
            "page": metadata.get("page", "unknown"),
            "source": metadata.get("source", "unknown"),
        })

    return chunks
