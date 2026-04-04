"""Two-phase RAG pipeline for document ingestion and retrieval.

Phase 1 (Ingestion): Load a document, chunk it using LangChain's
RecursiveCharacterTextSplitter, embed chunks using Google's
gemini-embedding-001, and store in Pinecone.

Phase 2 (Retrieval): Embed a query, find the top-K most semantically
relevant chunks in Pinecone filtered by document_id, and return
them with page numbers and source metadata.
"""

import logging
import google.generativeai as genai
from pinecone import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton clients — lazy-initialized on first use
# ---------------------------------------------------------------------------
_pinecone_client = None


def _get_pinecone_client():
    """Return a cached Pinecone client instance."""
    global _pinecone_client
    if _pinecone_client is None:
        _pinecone_client = Pinecone(api_key=settings.pinecone_api_key.get_secret_value())
    return _pinecone_client


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

def _embed_texts(texts: list[str]) -> list[list[float]]:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=texts,
        task_type="retrieval_document",
    )
    return result["embedding"]


def _embed_query_text(text: str) -> list[float]:
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]

# ---------------------------------------------------------------------------
# Pinecone client
# ---------------------------------------------------------------------------

def _get_index():
    return _get_pinecone_client().Index(settings.pinecone_index)


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------

def _load_file(file_path: str) -> list:
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
    Load a file, chunk it, embed the chunks, store in Pinecone.
    Returns the number of chunks stored.
    """
    logger.info("Ingesting document %s from %s", document_id, file_path)

    # 1. Load raw text
    raw_docs = _load_file(file_path)

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(raw_docs)

    if not chunks:
        raise ValueError("Document produced no chunks after splitting — file may be empty.")

    # 3. Extract text and metadata
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [
        {
            "document_id": document_id,
            "source": chunk.metadata.get("source", file_path),
            "page": str(chunk.metadata.get("page", "unknown")),
        }
        for chunk in chunks
    ]

    # 4. Embed all chunks
    embeddings = _embed_texts(texts)

    # 5. Store in Pinecone
    # Pinecone expects a list of (id, embedding, metadata) tuples
    index = _get_index()
    vectors = [
        {
            "id": f"{document_id}_{i}",
            "values": embeddings[i],
            "metadata": {**metadatas[i], "text": texts[i]},
        }
        for i in range(len(chunks))
    ]

    # Upsert in batches of 100 to stay within Pinecone limits
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[i:i + batch_size])

    logger.info("Stored %d chunks for document %s", len(chunks), document_id)
    return len(chunks)


# ---------------------------------------------------------------------------
# Phase 2 — Retrieval
# ---------------------------------------------------------------------------

async def retrieve_chunks(document_id: str, query: str) -> list[dict]:
    """
    Embed the query, find the top-K closest chunks in Pinecone.
    Returns a list of dicts with 'text', 'page', and 'source' keys.
    """
    logger.info("Retrieving chunks for document %s", document_id)

    query_embedding = _embed_query_text(query)

    index = _get_index()
    results = index.query(
        vector=query_embedding,
        top_k=settings.rag_top_k,
        filter={"document_id": {"$eq": document_id}},
        include_metadata=True,
    )

    chunks = []
    for match in results.matches:
        chunks.append({
            "text": match.metadata.get("text", ""),
            "page": match.metadata.get("page", "unknown"),
            "source": match.metadata.get("source", "unknown"),
        })

    return chunks
