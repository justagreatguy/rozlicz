"""Tasks package."""

from app.tasks.celery_app import celery_app
from app.tasks.document_tasks import (
    process_document_ocr,
    sync_document_to_ksef,
)
from app.tasks.ksef_tasks import (
    cleanup_expired_ksef_tokens,
    sync_user_ksef_invoices,
)
from app.tasks.tax_tasks import (
    calculate_monthly_tax,
    generate_annual_summary,
    submit_tax_return,
)

__all__ = [
    "celery_app",
    "process_document_ocr",
    "sync_document_to_ksef",
    "calculate_monthly_tax",
    "submit_tax_return",
    "generate_annual_summary",
    "sync_user_ksef_invoices",
    "cleanup_expired_ksef_tokens",
]
