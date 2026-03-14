import os
import logging
 
from pinecone import Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pathlib import Path
 
logger = logging.getLogger(__name__)
 
# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("RAG_TOP_K", "4"))
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "llm-analysis-service")
 
 
# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------
 
def _embed_texts(texts: list[str]) -> list[list[float]]:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=texts,
        task_type="retrieval_document",
    )
    return result["embedding"]


def _embed_query_text(text: str) -> list[float]:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]
 
# ---------------------------------------------------------------------------
# Pinecone client
# ---------------------------------------------------------------------------
 
def _get_index():
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    return pc.Index(PINECONE_INDEX)
 
 
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
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
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
        top_k=TOP_K,
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