"""Document processing tasks."""

from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.models.document import Document, DocumentStatus
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()

# Create async engine for tasks
engine = create_async_engine(str(settings.DATABASE_URL))
AsyncSessionLocal = sessionmaker(engine, class_=Base.metadata.__class__)


@celery_app.task(bind=True, max_retries=3)
def process_document_ocr(self, document_id: str) -> dict:
    """Process document OCR extraction.

    Args:
        document_id: Document ID to process

    Returns:
        Processing result
    """
    import asyncio

    return asyncio.run(_process_document_ocr_async(document_id))


async def _process_document_ocr_async(document_id: str) -> dict:
    """Async implementation of document OCR processing."""
    from sqlalchemy.ext.asyncio import AsyncSession

    async with AsyncSession(engine) as session:
        try:
            # Get document
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()

            if not document:
                logger.error("document_not_found", document_id=document_id)
                return {"status": "error", "error": "Document not found"}

            # Update status
            document.status = DocumentStatus.PROCESSING
            await session.commit()

            logger.info("ocr_processing_start", document_id=document_id)

            # TODO: Implement actual OCR processing
            # 1. Download file from storage
            # 2. Run OCR (e.g., Tesseract, AWS Textract, or Google Vision)
            # 3. Parse and extract invoice data
            # 4. Update document with extracted data

            # Placeholder: Simulate OCR processing
            extracted_data = {
                "invoice_number": None,  # Extracted from document
                "issue_date": None,
                "seller_nip": None,
                "buyer_nip": None,
                "net_amount": None,
                "vat_amount": None,
                "gross_amount": None,
                "vat_rate": None,
            }

            # Update document
            document.extracted_data = extracted_data
            document.status = DocumentStatus.PROCESSED
            document.processed_at = datetime.utcnow()

            await session.commit()

            logger.info("ocr_processing_complete", document_id=document_id)

            return {
                "status": "success",
                "document_id": document_id,
                "extracted_data": extracted_data,
            }

        except Exception as e:
            logger.error("ocr_processing_failed", document_id=document_id, error=str(e))

            # Update document status to error
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()
            if document:
                document.status = DocumentStatus.ERROR
                await session.commit()

            raise


@celery_app.task(bind=True, max_retries=3)
def sync_document_to_ksef(self, document_id: str) -> dict:
    """Sync document to KSeF.

    Args:
        document_id: Document ID to sync

    Returns:
        Sync result
    """
    import asyncio

    return asyncio.run(_sync_document_to_ksef_async(document_id))


async def _sync_document_to_ksef_async(document_id: str) -> dict:
    """Async implementation of KSeF sync."""
    from sqlalchemy.ext.asyncio import AsyncSession

    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = result.scalar_one_or_none()

            if not document:
                return {"status": "error", "error": "Document not found"}

            # TODO: Implement KSeF sync
            # 1. Get user KSeF token
            # 2. Generate FA_V2 XML
            # 3. Send to KSeF
            # 4. Store reference number

            document.status = DocumentStatus.SYNCED_TO_KSEF
            await session.commit()

            return {"status": "success", "document_id": document_id}

        except Exception as e:
            logger.error("ksef_sync_failed", document_id=document_id, error=str(e))
            raise
