"""Billing router for subscription and payment management."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.config import settings
from app.database import AsyncSession, get_db
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionTier
from app.models.user import User, UserRole
from app.routers.auth import get_current_admin, get_current_user
from app.services.stripe_service import StripeService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/subscription")
async def get_subscription(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get current user subscription."""
    from sqlalchemy import select

    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        return {
            "tier": SubscriptionTier.FREE,
            "status": "active",
        }

    return {
        "id": subscription.id,
        "tier": subscription.tier,
        "status": subscription.status,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "amount_pln": float(subscription.amount_pln) if subscription.amount_pln else None,
    }


@router.post("/checkout")
async def create_checkout_session(
    tier: SubscriptionTier,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create Stripe checkout session for subscription."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment processing not configured",
        )

    stripe_service = StripeService()

    try:
        session = await stripe_service.create_checkout_session(
            user=current_user,
            tier=tier,
            success_url="https://rozlicz.pl/success",
            cancel_url="https://rozlicz.pl/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        logger.error("checkout_session_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
        )


@router.post("/portal")
async def create_customer_portal(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create Stripe customer portal session."""
    from sqlalchemy import select

    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.stripe_customer_id.isnot(None),
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active paid subscription found",
        )

    stripe_service = StripeService()

    try:
        portal_session = await stripe_service.create_portal_session(
            customer_id=subscription.stripe_customer_id,
            return_url="https://rozlicz.pl/billing",
        )
        return {"portal_url": portal_session.url}
    except Exception as e:
        logger.error("portal_session_failed", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portal session",
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Handle Stripe webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured",
        )

    stripe_service = StripeService()

    try:
        event = await stripe_service.construct_webhook_event(
            payload, sig_header
        )
    except Exception as e:
        logger.error("webhook_signature_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # Process webhook event
    if event["type"] == "checkout.session.completed":
        await stripe_service.handle_checkout_completed(event["data"]["object"], db)
    elif event["type"] == "invoice.payment_succeeded":
        await stripe_service.handle_payment_succeeded(event["data"]["object"], db)
    elif event["type"] == "customer.subscription.deleted":
        await stripe_service.handle_subscription_cancelled(event["data"]["object"], db)

    return {"status": "ok"}


@router.get("/invoices")
async def list_invoices(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """List user invoices."""
    # TODO: Implement invoice listing
    return []


# Admin endpoints

@router.get("/admin/subscriptions")
async def list_all_subscriptions(
    current_user: Annotated[User, Depends(get_current_admin)],
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """List all subscriptions (admin only)."""
    from sqlalchemy import select

    result = await db.execute(
        select(Subscription).offset(skip).limit(limit)
    )
    subscriptions = result.scalars().all()

    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "tier": s.tier,
            "status": s.status,
        }
        for s in subscriptions
    ]
