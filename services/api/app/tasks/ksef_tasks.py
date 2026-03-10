"""KSeF synchronization tasks."""

from datetime import datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.config import settings
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.services.ksef_client import KSeFClient
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()

engine = create_async_engine(str(settings.DATABASE_URL))


@celery_app.task(bind=True, max_retries=3)
def sync_user_ksef_invoices(
    self,
    user_id: str,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    """Sync invoices from KSeF for a user.

    Args:
        user_id: User ID
        date_from: Start date (ISO format), defaults to 30 days ago
        date_to: End date (ISO format), defaults to today

    Returns:
        Sync result
    """
    import asyncio

    return asyncio.run(_sync_user_ksef_invoices_async(user_id, date_from, date_to))


async def _sync_user_ksef_invoices_async(
    user_id: str,
    date_from: str | None,
    date_to: str | None,
) -> dict:
    """Async implementation of KSeF sync."""
    async with AsyncSession(engine) as session:
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return {"status": "error", "error": "User not found"}

            if not user.ksef_token:
                return {"status": "error", "error": "KSeF token not configured"}

            # Parse dates
            if date_from:
                from_date = datetime.fromisoformat(date_from)
            else:
                from_date = datetime.utcnow() - timedelta(days=30)

            if date_to:
                to_date = datetime.fromisoformat(date_to)
            else:
                to_date = datetime.utcnow()

            logger.info(
                "ksef_sync_start",
                user_id=user_id,
                date_from=from_date,
                date_to=to_date,
            )

            # Connect to KSeF
            async with KSeFClient() as client:
                await client.authenticate(
                    nip=user.nip or "",
                    authorization_token=user.ksef_token,
                )

                # Query invoices
                response = await client.query_invoices(
                    date_from=from_date,
                    date_to=to_date,
                )

                invoices = response.get("invoices", [])
                synced_count = 0

                for invoice_data in invoices:
                    # TODO: Check if invoice already exists
                    # Create document record
                    document = Document(
                        user_id=user_id,
                        document_type="ksef_invoice",
                        ksef_number=invoice_data.get("ksefNumber"),
                        ksef_reference=invoice_data.get("referenceNumber"),
                        status=DocumentStatus.SYNCED_TO_KSEF,
                        ksef_synced_at=datetime.utcnow(),
                        # TODO: Parse and set other fields
                    )
                    session.add(document)
                    synced_count += 1

                await session.commit()

                logger.info(
                    "ksef_sync_complete",
                    user_id=user_id,
                    synced_count=synced_count,
                )

                return {
                    "status": "success",
                    "synced_count": synced_count,
                    "total_found": len(invoices),
                }

        except Exception as e:
            logger.error("ksef_sync_failed", error=str(e), user_id=user_id)
            raise


@celery_app.task
def cleanup_expired_ksef_tokens() -> dict:
    """Clean up expired KSeF tokens.

    Returns:
        Cleanup result
    """
    import asyncio

    return asyncio.run(_cleanup_expired_ksef_tokens_async())


async def _cleanup_expired_ksef_tokens_async() -> dict:
    """Async implementation of token cleanup."""
    async with AsyncSession(engine) as session:
        from sqlalchemy import update

        # Find users with expired tokens
        result = await session.execute(
            select(User).where(
                User.ksef_token_expires_at < datetime.utcnow(),
                User.ksef_token.isnot(None),
            )
        )
        users = result.scalars().all()

        cleared_count = 0
        for user in users:
            user.ksef_token = None
            user.ksef_token_expires_at = None
            cleared_count += 1

        await session.commit()

        logger.info("ksef_tokens_cleaned", cleared_count=cleared_count)

        return {
            "status": "success",
            "cleared_count": cleared_count,
        }
