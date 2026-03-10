"""Tax schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.tax import TaxForm, TaxReturnStatus


class TaxReturnBase(BaseModel):
    """Base tax return schema."""

    tax_form: TaxForm
    tax_year: int
    tax_month: int | None = None
    tax_quarter: int | None = None


class TaxReturnCreate(TaxReturnBase):
    """Tax return creation schema."""

    pass


class TaxReturnResponse(TaxReturnBase):
    """Tax return response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: TaxReturnStatus
    total_income: Decimal | None = None
    total_expenses: Decimal | None = None
    taxable_income: Decimal | None = None
    vat_output: Decimal | None = None
    vat_input: Decimal | None = None
    vat_due: Decimal | None = None
    tax_due: Decimal | None = None
    tax_paid: Decimal | None = None
    tax_to_pay: Decimal | None = None
    social_security_deduction: Decimal | None = None
    health_deduction: Decimal | None = None
    filing_deadline: date | None = None
    filed_at: datetime | None = None
    is_correction: bool
    created_at: datetime
    updated_at: datetime
    calculated_at: datetime | None = None


class TaxCalculationRequest(BaseModel):
    """Tax calculation request schema."""

    tax_form: TaxForm
    tax_year: int
    tax_month: int | None = None
    tax_quarter: int | None = None


class TaxCalculationResponse(BaseModel):
    """Tax calculation response schema."""

    tax_form: TaxForm
    tax_year: int
    tax_month: int | None = None
    tax_quarter: int | None = None
    total_income: Decimal
    total_expenses: Decimal
    taxable_income: Decimal
    vat_output: Decimal
    vat_input: Decimal
    vat_due: Decimal
    tax_due: Decimal
    social_security_deduction: Decimal | None = None
    health_deduction: Decimal | None = None
    calculation_breakdown: dict | None = None
