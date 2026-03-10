"""Document model for invoices and accounting documents."""

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class DocumentType(str, PyEnum):
    """Document type enumeration."""

    INVOICE_SALES = "invoice_sales"  # Faktura sprzedaży
    INVOICE_PURCHASE = "invoice_purchase"  # Faktura zakupu
    RECEIPT = "receipt"  # Paragon
    KSEF_INVOICE = "ksef_invoice"  # KSeF e-invoice
    EXPENSE = "expense"  # Wydatek
    OTHER = "other"


class DocumentStatus(str, PyEnum):
    """Document status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"
    SYNCED_TO_KSEF = "synced_to_ksef"


class VatRate(str, PyEnum):
    """Polish VAT rates."""

    RATE_23 = "23"
    RATE_8 = "8"
    RATE_5 = "5"
    RATE_0 = "0"
    EXEMPT = "zw"  # Zwolniony
    NOT_APPLICABLE = "np"  # Nie podlega


class Document(Base):
    """Document model for invoices and accounting records."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Document identification
    document_number: Mapped[str | None] = mapped_column(String(100))
    external_number: Mapped[str | None] = mapped_column(
        String(100),
        doc="Original invoice number from seller",
    )
    ksef_number: Mapped[str | None] = mapped_column(
        String(100),
        doc="KSeF reference number",
    )

    # Document type and status
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType),
        nullable=False,
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        default=DocumentStatus.PENDING,
        nullable=False,
    )

    # Dates
    issue_date: Mapped[date | None] = mapped_column(Date)
    sale_date: Mapped[date | None] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date)
    receipt_date: Mapped[date | None] = mapped_column(
        Date,
        doc="Date when document was received",
    )

    # Counterparty info
    counterparty_name: Mapped[str | None] = mapped_column(String(255))
    counterparty_nip: Mapped[str | None] = mapped_column(String(10))
    counterparty_address: Mapped[str | None] = mapped_column(Text)

    # Amounts
    net_amount: Mapped[float | None] = mapped_column(Numeric(15, 2))
    vat_amount: Mapped[float | None] = mapped_column(Numeric(15, 2))
    gross_amount: Mapped[float | None] = mapped_column(Numeric(15, 2))
    vat_rate: Mapped[VatRate | None] = mapped_column(Enum(VatRate))

    # Currency (for foreign invoices)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    exchange_rate: Mapped[float | None] = mapped_column(
        Numeric(10, 4),
        doc="NBP exchange rate for the day",
    )

    # File and extraction
    file_path: Mapped[str | None] = mapped_column(String(500))
    file_name: Mapped[str | None] = mapped_column(String(255))
    ocr_data: Mapped[dict | None] = mapped_column(
        JSONB,
        doc="Raw OCR extraction results",
    )
    extracted_data: Mapped[dict | None] = mapped_column(
        JSONB,
        doc="Structured extracted data",
    )

    # KSeF integration
    ksef_reference: Mapped[str | None] = mapped_column(String(255))
    ksef_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ksef_error: Mapped[str | None] = mapped_column(Text)

    # Tax year and month for reporting
    tax_year: Mapped[int | None] = mapped_column()
    tax_month: Mapped[int | None] = mapped_column()

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, type={self.document_type}, status={self.status})>"
