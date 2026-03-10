"""Tax calculation and filing tasks."""

from datetime import datetime
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base
from app.models.tax import TaxForm, TaxReturn, TaxReturnStatus
from app.models.user import User
from app.services.tax_calculator import TaxCalculator
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()

# Create async engine for tasks
engine = create_async_engine(str(settings.DATABASE_URL))


@celery_app.task(bind=True, max_retries=3)
def calculate_monthly_tax(
    self,
    user_id: str,
    tax_form: str,
    tax_year: int,
    tax_month: int,
) -> dict:
    """Calculate tax for a month and create/update tax return.

    Args:
        user_id: User ID
        tax_form: Tax form type
        tax_year: Tax year
        tax_month: Tax month

    Returns:
        Calculation result
    """
    import asyncio

    return asyncio.run(
        _calculate_monthly_tax_async(user_id, tax_form, tax_year, tax_month)
    )


async def _calculate_monthly_tax_async(
    user_id: str,
    tax_form: str,
    tax_year: int,
    tax_month: int,
) -> dict:
    """Async implementation of monthly tax calculation."""
    async with AsyncSession(engine) as session:
        try:
            # Get user
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                return {"status": "error", "error": "User not found"}

            # Calculate tax
            calculator = TaxCalculator(session)
            calculation = await calculator.calculate(
                user=user,
                tax_form=TaxForm(tax_form),
                tax_year=tax_year,
                tax_month=tax_month,
            )

            # Find existing tax return
            result = await session.execute(
                select(TaxReturn).where(
                    TaxReturn.user_id == user_id,
                    TaxReturn.tax_form == tax_form,
                    TaxReturn.tax_year == tax_year,
                    TaxReturn.tax_month == tax_month,
                )
            )
            tax_return = result.scalar_one_or_none()

            if tax_return:
                # Update existing
                for key, value in calculation.items():
                    if hasattr(tax_return, key):
                        setattr(tax_return, key, value)
                tax_return.status = TaxReturnStatus.CALCULATED
                tax_return.calculated_at = datetime.utcnow()
            else:
                # Create new
                tax_return = TaxReturn(
                    user_id=user_id,
                    tax_form=TaxForm(tax_form),
                    tax_year=tax_year,
                    tax_month=tax_month,
                    status=TaxReturnStatus.CALCULATED,
                    calculation_data=calculation,
                    calculated_at=datetime.utcnow(),
                    **{k: v for k, v in calculation.items() if k not in [
                        "tax_form", "tax_year", "tax_month", "tax_quarter", "calculation_breakdown"
                    ]},
                )
                session.add(tax_return)

            await session.commit()

            logger.info(
                "tax_calculated",
                tax_return_id=tax_return.id,
                user_id=user_id,
                year=tax_year,
                month=tax_month,
            )

            return {
                "status": "success",
                "tax_return_id": str(tax_return.id),
                "calculation": calculation,
            }

        except Exception as e:
            logger.error("tax_calculation_failed", error=str(e), user_id=user_id)
            raise


@celery_app.task(bind=True, max_retries=2)
def submit_tax_return(
    self,
    tax_return_id: str,
) -> dict:
    """Submit tax return to tax authority.

    Args:
        tax_return_id: Tax return ID

    Returns:
        Submission result
    """
    import asyncio

    return asyncio.run(_submit_tax_return_async(tax_return_id))


async def _submit_tax_return_async(tax_return_id: str) -> dict:
    """Async implementation of tax return submission."""
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(TaxReturn).where(TaxReturn.id == tax_return_id)
            )
            tax_return = result.scalar_one_or_none()

            if not tax_return:
                return {"status": "error", "error": "Tax return not found"}

            # TODO: Implement actual submission to e-Deklaracje or KSeF
            # This would involve:
            # 1. Generating XML in the correct format
            # 2. Signing with qualified electronic signature
            # 3. Submitting to tax authority API
            # 4. Polling for response
            # 5. Storing confirmation (UPO)

            logger.info(
                "tax_return_submitted",
                tax_return_id=tax_return_id,
                user_id=tax_return.user_id,
            )

            tax_return.status = TaxReturnStatus.FILED
            tax_return.filed_at = datetime.utcnow()
            await session.commit()

            return {
                "status": "success",
                "tax_return_id": tax_return_id,
                "reference_number": "TODO",  # Would come from tax authority
            }

        except Exception as e:
            logger.error("tax_return_submission_failed", error=str(e))
            raise


@celery_app.task
def generate_annual_summary(
    user_id: str,
    tax_year: int,
) -> dict:
    """Generate annual tax summary for user.

    Args:
        user_id: User ID
        tax_year: Tax year

    Returns:
        Summary data
    """
    import asyncio

    return asyncio.run(_generate_annual_summary_async(user_id, tax_year))


async def _generate_annual_summary_async(
    user_id: str,
    tax_year: int,
) -> dict:
    """Async implementation of annual summary generation."""
    async with AsyncSession(engine) as session:
        from sqlalchemy import func

        result = await session.execute(
            select(
                func.count(TaxReturn.id).label("total_returns"),
                func.sum(TaxReturn.tax_due).label("total_tax"),
                func.sum(TaxReturn.vat_due).label("total_vat"),
                func.sum(TaxReturn.total_income).label("total_income"),
                func.sum(TaxReturn.total_expenses).label("total_expenses"),
            ).where(
                TaxReturn.user_id == user_id,
                TaxReturn.tax_year == tax_year,
            )
        )
        row = result.one()

        return {
            "user_id": user_id,
            "tax_year": tax_year,
            "total_returns": row.total_returns or 0,
            "total_tax_due": float(row.total_tax) if row.total_tax else 0,
            "total_vat_due": float(row.total_vat) if row.total_vat else 0,
            "total_income": float(row.total_income) if row.total_income else 0,
            "total_expenses": float(row.total_expenses) if row.total_expenses else 0,
        }
