import os
import uuid
import shutil
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.models import Document
from app.services.rag_pipeline import ingest_document
from app.core.config import settings

router = APIRouter(prefix="/v1/documents", tags=["documents"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv"}

logger = logging.getLogger(__name__)

@router.post("", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Upload a document for RAG ingestion.

    1. Validates file type and size
    2. Sanitizes filename to prevent path traversal
    3. Saves file to disk
    4. Creates a Document record in Postgres (status=processing)
    5. Runs the RAG ingestion pipeline (chunking + embedding + Pinecone)
    6. Updates the Document record (status=ready, chunk_count=N)

    Returns the document_id — pass this into /v1/analysis to query against it.
    """
    # 1. Validate filename exists
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # 2. Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(file.filename)

    # 3. Validate extension
    ext = Path(safe_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 4. Validate file size
    contents = await file.read()
    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_upload_bytes / (1024 * 1024):.0f} MB"
        )

    # 5. Save file to disk
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    document_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{document_id}{ext}"

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # 6. Create DB record
    doc = Document(
        id=uuid.UUID(document_id),
        filename=safe_filename,
        file_type=ext.lstrip("."),
        status="processing",
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    # 7. Run ingestion
    try:
        chunk_count = await ingest_document(str(file_path), document_id)

        # 8. Mark ready
        doc.status = "ready"
        doc.chunk_count = chunk_count
        await session.commit()

        return {
            "document_id": document_id,
            "filename": safe_filename,
            "status": "ready",
            "chunk_count": chunk_count,
        }

    except Exception:
        logger.exception("Ingestion failed for document %s", document_id)
        doc.status = "failed"
        await session.commit()
        raise HTTPException(status_code=500, detail="Document ingestion failed")


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Check the status of an uploaded document."""
    result = await session.execute(
        select(Document).where(Document.id == uuid.UUID(document_id))
    )
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": str(doc.id),
        "filename": doc.filename,
        "status": doc.status,
        "chunk_count": doc.chunk_count,
        "created_at": doc.created_at,
    }
