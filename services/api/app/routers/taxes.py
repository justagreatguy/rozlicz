"""Taxes router for tax calculations and returns."""

from datetime import date
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import AsyncSession, get_db
from app.models.tax import TaxForm, TaxReturn, TaxReturnStatus
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.tax import (
    TaxCalculationRequest,
    TaxCalculationResponse,
    TaxReturnCreate,
    TaxReturnResponse,
)
from app.services.tax_calculator import TaxCalculator

logger = structlog.get_logger()
router = APIRouter()


@router.get("/returns", response_model=list[TaxReturnResponse])
async def list_tax_returns(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    tax_year: int | None = None,
    tax_form: TaxForm | None = None,
    status: TaxReturnStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[TaxReturn]:
    """List user tax returns."""
    from sqlalchemy import select

    query = select(TaxReturn).where(TaxReturn.user_id == current_user.id)

    if tax_year:
        query = query.where(TaxReturn.tax_year == tax_year)
    if tax_form:
        query = query.where(TaxReturn.tax_form == tax_form)
    if status:
        query = query.where(TaxReturn.status == status)

    query = query.order_by(TaxReturn.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/returns/{return_id}", response_model=TaxReturnResponse)
async def get_tax_return(
    return_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> TaxReturn:
    """Get a specific tax return."""
    from sqlalchemy import select

    result = await db.execute(
        select(TaxReturn).where(
            TaxReturn.id == str(return_id),
            TaxReturn.user_id == current_user.id,
        )
    )
    tax_return = result.scalar_one_or_none()

    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )

    return tax_return


@router.post("/calculate", response_model=TaxCalculationResponse)
async def calculate_tax(
    request: TaxCalculationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Calculate tax for a given period without saving."""
    calculator = TaxCalculator(db)

    try:
        result = await calculator.calculate(
            user=current_user,
            tax_form=request.tax_form,
            tax_year=request.tax_year,
            tax_month=request.tax_month,
            tax_quarter=request.tax_quarter,
        )
        return result
    except Exception as e:
        logger.error(
            "tax_calculation_failed",
            error=str(e),
            user_id=current_user.id,
            tax_form=request.tax_form,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tax calculation failed",
        )


@router.post("/returns", response_model=TaxReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_tax_return(
    data: TaxReturnCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> TaxReturn:
    """Create a new tax return."""
    calculator = TaxCalculator(db)

    # Calculate tax
    calculation = await calculator.calculate(
        user=current_user,
        tax_form=data.tax_form,
        tax_year=data.tax_year,
        tax_month=data.tax_month,
        tax_quarter=data.tax_quarter,
    )

    # Create tax return record
    tax_return = TaxReturn(
        user_id=current_user.id,
        tax_form=data.tax_form,
        tax_year=data.tax_year,
        tax_month=data.tax_month,
        tax_quarter=data.tax_quarter,
        status=TaxReturnStatus.CALCULATED,
        **calculation,
        calculation_data=calculation,
    )

    db.add(tax_return)
    await db.commit()
    await db.refresh(tax_return)

    logger.info(
        "tax_return_created",
        tax_return_id=tax_return.id,
        user_id=current_user.id,
        tax_form=data.tax_form,
    )

    return tax_return


@router.post("/returns/{return_id}/recalculate", response_model=TaxReturnResponse)
async def recalculate_tax_return(
    return_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> TaxReturn:
    """Recalculate a tax return."""
    from sqlalchemy import select

    result = await db.execute(
        select(TaxReturn).where(
            TaxReturn.id == str(return_id),
            TaxReturn.user_id == current_user.id,
        )
    )
    tax_return = result.scalar_one_or_none()

    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )

    if tax_return.status == TaxReturnStatus.FILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot recalculate filed tax return",
        )

    # Recalculate
    calculator = TaxCalculator(db)
    calculation = await calculator.calculate(
        user=current_user,
        tax_form=tax_return.tax_form,
        tax_year=tax_return.tax_year,
        tax_month=tax_return.tax_month,
        tax_quarter=tax_return.tax_quarter,
    )

    # Update tax return
    for key, value in calculation.items():
        setattr(tax_return, key, value)

    tax_return.calculation_data = calculation
    tax_return.status = TaxReturnStatus.CALCULATED

    await db.commit()
    await db.refresh(tax_return)

    logger.info(
        "tax_return_recalculated",
        tax_return_id=tax_return.id,
        user_id=current_user.id,
    )

    return tax_return


@router.post("/returns/{return_id}/submit")
async def submit_tax_return(
    return_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit tax return for filing."""
    from sqlalchemy import select

    result = await db.execute(
        select(TaxReturn).where(
            TaxReturn.id == str(return_id),
            TaxReturn.user_id == current_user.id,
        )
    )
    tax_return = result.scalar_one_or_none()

    if not tax_return:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax return not found",
        )

    if tax_return.status not in [TaxReturnStatus.CALCULATED, TaxReturnStatus.DRAFT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit tax return with status {tax_return.status}",
        )

    # TODO: Integrate with e-Deklaracje or KSeF for filing
    tax_return.status = TaxReturnStatus.READY_TO_FILE
    await db.commit()

    logger.info(
        "tax_return_submitted",
        tax_return_id=tax_return.id,
        user_id=current_user.id,
    )

    return {
        "message": "Tax return submitted for filing",
        "tax_return_id": tax_return.id,
        "status": tax_return.status,
    }


@router.get("/summary")
async def get_tax_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    tax_year: int = Query(..., ge=2020, le=2100),
) -> dict:
    """Get annual tax summary."""
    from sqlalchemy import func, select

    result = await db.execute(
        select(
            func.count(TaxReturn.id).label("total_returns"),
            func.sum(TaxReturn.tax_due).label("total_tax_due"),
            func.sum(TaxReturn.vat_due).label("total_vat_due"),
            func.sum(TaxReturn.total_income).label("total_income"),
            func.sum(TaxReturn.total_expenses).label("total_expenses"),
        ).where(
            TaxReturn.user_id == current_user.id,
            TaxReturn.tax_year == tax_year,
        )
    )
    row = result.one()

    return {
        "tax_year": tax_year,
        "total_returns": row.total_returns or 0,
        "total_tax_due": float(row.total_tax_due) if row.total_tax_due else 0,
        "total_vat_due": float(row.total_vat_due) if row.total_vat_due else 0,
        "total_income": float(row.total_income) if row.total_income else 0,
        "total_expenses": float(row.total_expenses) if row.total_expenses else 0,
        "taxable_income": float(row.total_income or 0) - float(row.total_expenses or 0),
    }


@router.get("/deadlines")
async def get_tax_deadlines(
    current_user: Annotated[User, Depends(get_current_user)],
    year: int = Query(default_factory=lambda: date.today().year),
) -> list[dict]:
    """Get upcoming tax deadlines."""
    # TODO: Calculate based on user's tax form and current date
    deadlines = [
        {
            "form": TaxForm.VAT_7,
            "due_date": f"{year}-01-25",
            "description": "VAT-7 for December",
        },
        {
            "form": TaxForm.PIT_5,
            "due_date": f"{year}-01-20",
            "description": "PIT-5 for December",
        },
    ]
    return deadlines
