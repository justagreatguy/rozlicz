"""Documents router for invoice management."""

from datetime import date
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.database import AsyncSession, get_db
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.tasks.document_tasks import process_document_ocr

logger = structlog.get_logger()
router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    document_type: DocumentType | None = None,
    status: DocumentStatus | None = None,
    tax_year: int | None = None,
    tax_month: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[Document]:
    """List user documents with optional filters."""
    from sqlalchemy import select

    query = select(Document).where(Document.user_id == current_user.id)

    if document_type:
        query = query.where(Document.document_type == document_type)
    if status:
        query = query.where(Document.status == status)
    if tax_year:
        query = query.where(Document.tax_year == tax_year)
    if tax_month:
        query = query.where(Document.tax_month == tax_month)

    query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Get a specific document."""
    from sqlalchemy import select

    result = await db.execute(
        select(Document).where(
            Document.id == str(document_id),
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Annotated[UploadFile, File()],
    document_type: DocumentType,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Upload a new document for processing."""
    # Validate file type
    allowed_types = ["application/pdf", "image/jpeg", "image/png", "image/tiff"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}",
        )

    # TODO: Upload file to storage (S3/minio)
    # For now, store filename only
    file_path = f"uploads/{current_user.id}/{file.filename}"

    # Create document record
    document = Document(
        user_id=current_user.id,
        document_type=document_type,
        file_path=file_path,
        file_name=file.filename,
        status=DocumentStatus.PENDING,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    # Queue OCR processing
    process_document_ocr.delay(str(document.id))

    logger.info(
        "document_uploaded",
        document_id=document.id,
        user_id=current_user.id,
        type=document_type,
    )

    return document


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    data: DocumentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Create a document manually (without file upload)."""
    document = Document(
        user_id=current_user.id,
        **data.model_dump(exclude_unset=True),
        status=DocumentStatus.PROCESSED,
    )

    # Set tax period from issue date
    if document.issue_date:
        document.tax_year = document.issue_date.year
        document.tax_month = document.issue_date.month

    db.add(document)
    await db.commit()
    await db.refresh(document)

    logger.info(
        "document_created",
        document_id=document.id,
        user_id=current_user.id,
    )

    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Document:
    """Update a document."""
    from sqlalchemy import select

    result = await db.execute(
        select(Document).where(
            Document.id == str(document_id),
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    # Recalculate tax period if issue_date changed
    if "issue_date" in update_data and document.issue_date:
        document.tax_year = document.issue_date.year
        document.tax_month = document.issue_date.month

    await db.commit()
    await db.refresh(document)

    logger.info(
        "document_updated",
        document_id=document.id,
        user_id=current_user.id,
    )

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a document."""
    from sqlalchemy import select

    result = await db.execute(
        select(Document).where(
            Document.id == str(document_id),
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    await db.delete(document)
    await db.commit()

    logger.info(
        "document_deleted",
        document_id=document_id,
        user_id=current_user.id,
    )


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get download URL for a document."""
    from sqlalchemy import select

    result = await db.execute(
        select(Document).where(
            Document.id == str(document_id),
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # TODO: Generate presigned URL from storage
    return {
        "download_url": f"/storage/{document.file_path}",
        "filename": document.file_name,
    }
