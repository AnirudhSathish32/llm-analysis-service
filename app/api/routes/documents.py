import os
import uuid
import shutil
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.models import Document
from app.services.rag_pipeline import ingest_document

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

    1. Validates file type
    2. Saves file to disk
    3. Creates a Document record in Postgres (status=processing)
    4. Runs the RAG ingestion pipeline (chunking + embedding + ChromaDB)
    5. Updates the Document record (status=ready, chunk_count=N)

    Returns the document_id — pass this into /v1/analysis to query against it.
    """
    # 1. Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Save file to disk
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    document_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{document_id}{ext}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Create DB record
    doc = Document(
        id=uuid.UUID(document_id),
        filename=file.filename,
        file_type=ext.lstrip("."),
        status="processing",
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    # 4. Run ingestion
    try:
        chunk_count = await ingest_document(str(file_path), document_id)

        # 5. Mark ready
        doc.status = "ready"
        doc.chunk_count = chunk_count
        await session.commit()

        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "ready",
            "chunk_count": chunk_count,
        }

    except Exception as e:
        import traceback
        logger.error("Ingestion failed: %s", traceback.format_exc())
        doc.status = "failed"
        await session.commit()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Check the status of an uploaded document."""
    from sqlalchemy import select
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
