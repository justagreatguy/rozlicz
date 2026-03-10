"""Tax calculator for Polish JDG taxation."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, DocumentType, VatRate
from app.models.tax import TaxForm
from app.models.user import User

if TYPE_CHECKING:
    pass

logger = structlog.get_logger()

# Tax constants for 2024 (update annually)
TAX_SCALE_THRESHOLD = Decimal("120000")  # First tax threshold
TAX_RATE_1 = Decimal("0.12")  # 12% up to threshold
TAX_RATE_2 = Decimal("0.32")  # 32% above threshold
LINEAR_TAX_RATE = Decimal("0.19")  # 19% flat rate

# ZUS contributions (2024 approximate values)
ZUS_SOCIAL_MINIMUM = Decimal("1247.92")  # Minimum social contribution
ZUS_HEALTH_TAX_SCALE = Decimal("465.63")  # Health contribution for tax scale
ZUS_HEALTH_LINEAR = Decimal("381.78")  # Health contribution for linear (deductible)
ZUS_HEALTH_FLAT = Decimal("419.02")  # Health contribution for flat rate (deductible)


class TaxCalculator:
    """Calculator for Polish JDG taxes."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize calculator.

        Args:
            db: Database session
        """
        self.db = db

    async def calculate(
        self,
        user: User,
        tax_form: TaxForm,
        tax_year: int,
        tax_month: int | None = None,
        tax_quarter: int | None = None,
    ) -> dict:
        """Calculate tax for given period.

        Args:
            user: The user
            tax_form: Type of tax form
            tax_year: Tax year
            tax_month: Tax month (for monthly forms)
            tax_quarter: Tax quarter (for quarterly forms)

        Returns:
            Dictionary with calculation results
        """
        logger.info(
            "tax_calculation_start",
            user_id=user.id,
            tax_form=tax_form,
            year=tax_year,
            month=tax_month,
            quarter=tax_quarter,
        )

        # Determine date range
        date_from, date_to = self._get_date_range(
            tax_year, tax_month, tax_quarter
        )

        # Get documents for period
        documents = await self._get_documents(user.id, date_from, date_to)

        # Calculate based on tax form
        if tax_form in [TaxForm.PIT_5, TaxForm.PIT_36]:
            result = await self._calculate_tax_scale(
                documents, user, tax_year, tax_month
            )
        elif tax_form in [TaxForm.PIT_5L, TaxForm.PIT_36L]:
            result = await self._calculate_linear(
                documents, user, tax_year, tax_month
            )
        elif tax_form == TaxForm.PIT_28:
            result = await self._calculate_flat_rate(
                documents, user, tax_year, tax_month
            )
        elif tax_form in [TaxForm.VAT_7, TaxForm.VAT_7K, TaxForm.JPK_V7M, TaxForm.JPK_V7K]:
            result = await self._calculate_vat(documents)
        else:
            raise ValueError(f"Unsupported tax form: {tax_form}")

        result.update({
            "tax_form": tax_form,
            "tax_year": tax_year,
            "tax_month": tax_month,
            "tax_quarter": tax_quarter,
        })

        return result

    def _get_date_range(
        self,
        year: int,
        month: int | None,
        quarter: int | None,
    ) -> tuple[date, date]:
        """Calculate date range from tax period."""
        if month:
            from_date = date(year, month, 1)
            if month == 12:
                to_date = date(year + 1, 1, 1)
            else:
                to_date = date(year, month + 1, 1)
        elif quarter:
            month_start = (quarter - 1) * 3 + 1
            from_date = date(year, month_start, 1)
            if quarter == 4:
                to_date = date(year + 1, 1, 1)
            else:
                to_date = date(year, month_start + 3, 1)
        else:
            # Annual
            from_date = date(year, 1, 1)
            to_date = date(year + 1, 1, 1)

        return from_date, to_date

    async def _get_documents(
        self,
        user_id: str,
        date_from: date,
        date_to: date,
    ) -> list[Document]:
        """Get documents for user in date range."""
        result = await self.db.execute(
            select(Document).where(
                Document.user_id == user_id,
                Document.issue_date >= date_from,
                Document.issue_date < date_to,
                Document.status.in_(["processed", "synced_to_ksef"]),
            )
        )
        return list(result.scalars().all())

    async def _calculate_tax_scale(
        self,
        documents: list[Document],
        user: User,
        year: int,
        month: int | None,
    ) -> dict:
        """Calculate tax using progressive scale (skala podatkowa)."""
        # Income and expenses
        sales = sum(
            (d.gross_amount or 0)
            for d in documents
            if d.document_type == DocumentType.INVOICE_SALES
        )
        expenses = sum(
            (d.gross_amount or 0)
            for d in documents
            if d.document_type == DocumentType.INVOICE_PURCHASE
        )

        taxable_income = max(Decimal("0"), Decimal(str(sales)) - Decimal(str(expenses)))

        # Calculate tax (simplified - full implementation needs cumulative calculation)
        if taxable_income <= TAX_SCALE_THRESHOLD:
            tax = taxable_income * TAX_RATE_1
        else:
            tax = (TAX_SCALE_THRESHOLD * TAX_RATE_1) + (
                (taxable_income - TAX_SCALE_THRESHOLD) * TAX_RATE_2
            )

        # TODO: Deduct social security contributions
        # tax -= social_contributions

        return {
            "total_income": Decimal(str(sales)),
            "total_expenses": Decimal(str(expenses)),
            "taxable_income": taxable_income,
            "tax_due": tax.quantize(Decimal("0.01")),
            "tax_to_pay": tax.quantize(Decimal("0.01")),
            "social_security_deduction": None,  # TODO
            "health_deduction": None,  # Not deductible in tax scale
            "calculation_breakdown": {
                "rate_1": TAX_RATE_1,
                "rate_2": TAX_RATE_2,
                "threshold": TAX_SCALE_THRESHOLD,
            },
        }

    async def _calculate_linear(
        self,
        documents: list[Document],
        user: User,
        year: int,
        month: int | None,
    ) -> dict:
        """Calculate tax using linear rate (19%)."""
        sales = sum(
            (d.gross_amount or 0)
            for d in documents
            if d.document_type == DocumentType.INVOICE_SALES
        )
        expenses = sum(
            (d.gross_amount or 0)
            for d in documents
            if d.document_type == DocumentType.INVOICE_PURCHASE
        )

        taxable_income = max(Decimal("0"), Decimal(str(sales)) - Decimal(str(expenses)))
        tax = taxable_income * LINEAR_TAX_RATE

        # Health contribution is deductible in linear tax
        health_deduction = ZUS_HEALTH_LINEAR if month else ZUS_HEALTH_LINEAR * 12
        tax -= health_deduction

        return {
            "total_income": Decimal(str(sales)),
            "total_expenses": Decimal(str(expenses)),
            "taxable_income": taxable_income,
            "tax_due": max(Decimal("0"), tax).quantize(Decimal("0.01")),
            "tax_to_pay": max(Decimal("0"), tax).quantize(Decimal("0.01")),
            "social_security_deduction": None,  # TODO
            "health_deduction": health_deduction,
            "calculation_breakdown": {
                "rate": LINEAR_TAX_RATE,
            },
        }

    async def _calculate_flat_rate(
        self,
        documents: list[Document],
        user: User,
        year: int,
        month: int | None,
    ) -> dict:
        """Calculate tax using flat rate (ryczałt).

        Flat rate is calculated on revenue (przychód), not profit.
        Different rates apply based on business type.
        """
        revenue = sum(
            (d.net_amount or 0)
            for d in documents
            if d.document_type == DocumentType.INVOICE_SALES
        )

        # Default flat rate 12% (varies by business type)
        flat_rate = Decimal("0.12")
        tax = Decimal(str(revenue)) * flat_rate

        # Health contribution deduction
        health_deduction = ZUS_HEALTH_FLAT if month else ZUS_HEALTH_FLAT * 12

        return {
            "total_income": Decimal(str(revenue)),
            "total_expenses": Decimal("0"),  # No expense deduction in flat rate
            "taxable_income": Decimal(str(revenue)),
            "tax_due": max(Decimal("0"), tax - health_deduction).quantize(Decimal("0.01")),
            "tax_to_pay": max(Decimal("0"), tax - health_deduction).quantize(Decimal("0.01")),
            "social_security_deduction": None,
            "health_deduction": health_deduction,
            "calculation_breakdown": {
                "flat_rate": flat_rate,
                "revenue": revenue,
            },
        }

    async def _calculate_vat(self, documents: list[Document]) -> dict:
        """Calculate VAT."""
        vat_output = Decimal("0")  # VAT on sales
        vat_input = Decimal("0")  # VAT on purchases

        for doc in documents:
            if doc.document_type == DocumentType.INVOICE_SALES:
                vat_output += Decimal(str(doc.vat_amount or 0))
            elif doc.document_type == DocumentType.INVOICE_PURCHASE:
                vat_input += Decimal(str(doc.vat_amount or 0))

        vat_due = vat_output - vat_input

        return {
            "total_income": Decimal("0"),
            "total_expenses": Decimal("0"),
            "taxable_income": Decimal("0"),
            "vat_output": vat_output,
            "vat_input": vat_input,
            "vat_due": vat_due,
            "tax_due": Decimal("0"),
            "tax_to_pay": vat_due.quantize(Decimal("0.01")),
            "calculation_breakdown": {
                "vat_output": vat_output,
                "vat_input": vat_input,
            },
        }
