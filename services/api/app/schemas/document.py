"""Document schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus, DocumentType, VatRate


class DocumentBase(BaseModel):
    """Base document schema."""

    document_number: str | None = None
    external_number: str | None = None
    document_type: DocumentType
    issue_date: date | None = None
    sale_date: date | None = None
    due_date: date | None = None
    receipt_date: date | None = None
    counterparty_name: str | None = None
    counterparty_nip: str | None = Field(None, pattern=r"^\d{10}$")
    counterparty_address: str | None = None
    net_amount: Decimal | None = None
    vat_amount: Decimal | None = None
    gross_amount: Decimal | None = None
    vat_rate: VatRate | None = None
    currency: str = "PLN"


class DocumentCreate(DocumentBase):
    """Document creation schema."""

    pass


class DocumentUpdate(BaseModel):
    """Document update schema."""

    document_number: str | None = None
    external_number: str | None = None
    issue_date: date | None = None
    sale_date: date | None = None
    due_date: date | None = None
    counterparty_name: str | None = None
    counterparty_nip: str | None = None
    counterparty_address: str | None = None
    net_amount: Decimal | None = None
    vat_amount: Decimal | None = None
    gross_amount: Decimal | None = None
    vat_rate: VatRate | None = None


class DocumentResponse(DocumentBase):
    """Document response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: DocumentStatus
    ksef_number: str | None = None
    ksef_reference: str | None = None
    ksef_synced_at: datetime | None = None
    tax_year: int | None = None
    tax_month: int | None = None
    file_name: str | None = None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None = None
