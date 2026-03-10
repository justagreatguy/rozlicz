"""Tax model for tax calculations and returns."""

from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class TaxForm(str, PyEnum):
    """Polish tax form types for JDG."""

    PIT_5 = "pit_5"  # Zaliczka na PIT (miesięczna/kwartał)
    PIT_5L = "pit_5l"  # Zaliczka na PIT - liniowy
    PIT_28 = "pit_28"  # Ryczałt od przychodów ewidencjonowanych
    PIT_36 = "pit_36"  # PIT roczny - skala podatkowa
    PIT_36L = "pit_36l"  # PIT roczny - liniowy
    PIT_28_ANNUAL = "pit_28_annual"  # PIT roczny - ryczałt
    VAT_7 = "vat_7"  # Deklaracja VAT miesięczna
    VAT_7K = "vat_7k"  # Deklaracja VAT kwartalna
    JPK_V7M = "jpk_v7m"  # Jednolity plik kontrolny - VAT miesięczny
    JPK_V7K = "jpk_v7k"  # JPK VAT kwartalny


class TaxReturnStatus(str, PyEnum):
    """Tax return status enumeration."""

    DRAFT = "draft"
    CALCULATED = "calculated"
    PENDING_APPROVAL = "pending_approval"
    READY_TO_FILE = "ready_to_file"
    FILED = "filed"
    PAID = "paid"
    CORRECTED = "corrected"


class TaxReturn(Base):
    """Tax return model for storing tax calculations."""

    __tablename__ = "tax_returns"

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

    # Tax period
    tax_form: Mapped[TaxForm] = mapped_column(Enum(TaxForm), nullable=False)
    tax_year: Mapped[int] = mapped_column(nullable=False)
    tax_month: Mapped[int | None] = mapped_column()  # null for annual returns
    tax_quarter: Mapped[int | None] = mapped_column()  # for quarterly returns

    # Status
    status: Mapped[TaxReturnStatus] = mapped_column(
        Enum(TaxReturnStatus),
        default=TaxReturnStatus.DRAFT,
        nullable=False,
    )

    # Income and expenses
    total_income: Mapped[float | None] = mapped_column(Numeric(15, 2))
    total_expenses: Mapped[float | None] = mapped_column(Numeric(15, 2))
    taxable_income: Mapped[float | None] = mapped_column(Numeric(15, 2))

    # VAT calculations
    vat_output: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        doc="VAT on sales (output tax)",
    )
    vat_input: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        doc="VAT on purchases (input tax)",
    )
    vat_due: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        doc="VAT payable (output - input)",
    )

    # Income tax calculations
    tax_due: Mapped[float | None] = mapped_column(Numeric(15, 2))
    tax_paid: Mapped[float | None] = mapped_column(Numeric(15, 2), default=0)
    tax_to_pay: Mapped[float | None] = mapped_column(Numeric(15, 2))

    # Deductions
    social_security_deduction: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        doc="ZUS social contribution deduction",
    )
    health_deduction: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        doc="Health insurance deduction (ryczałt)",
    )

    # Filing info
    filing_deadline: Mapped[date | None] = mapped_column(Date)
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    filed_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
    )

    # Calculation details
    calculation_data: Mapped[dict | None] = mapped_column(
        JSONB,
        doc="Detailed calculation breakdown",
    )
    documents_included: Mapped[list | None] = mapped_column(
        JSONB,
        doc="List of document IDs included",
    )

    # Correction info
    is_correction: Mapped[bool] = mapped_column(Boolean, default=False)
    original_return_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("tax_returns.id"),
    )
    correction_reason: Mapped[str | None] = mapped_column(Text)

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
    calculated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tax_returns",
        foreign_keys=[user_id],
    )

    def __repr__(self) -> str:
        return (
            f"<TaxReturn(id={self.id}, form={self.tax_form}, "
            f"year={self.tax_year}, status={self.status})>"
        )
