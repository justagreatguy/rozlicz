"""Stripe service for payment processing."""

from typing import Any

import stripe
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionTier
from app.models.user import User

logger = structlog.get_logger()

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Stripe service for subscription and payment management."""

    def __init__(self) -> None:
        """Initialize Stripe service."""
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY

    async def create_checkout_session(
        self,
        user: User,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str,
    ) -> stripe.checkout.Session:
        """Create Stripe checkout session for subscription.

        Args:
            user: The user subscribing
            tier: Subscription tier
            success_url: Redirect URL after successful payment
            cancel_url: Redirect URL after cancellation

        Returns:
            Stripe checkout session
        """
        # Map tier to price ID
        price_id_map = {
            SubscriptionTier.BASIC: settings.STRIPE_PRICE_ID_BASIC,
            SubscriptionTier.PRO: settings.STRIPE_PRICE_ID_PRO,
        }

        price_id = price_id_map.get(tier)
        if not price_id:
            raise ValueError(f"No price ID configured for tier {tier}")

        # Create or get customer
        customer_id = await self._get_or_create_customer(user)

        logger.info(
            "stripe_checkout_create",
            user_id=user.id,
            tier=tier,
            customer_id=customer_id,
        )

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(user.id),
                "tier": tier.value,
            },
        )

        return session

    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> stripe.billing_portal.Session:
        """Create Stripe customer portal session.

        Args:
            customer_id: Stripe customer ID
            return_url: Return URL after portal session

        Returns:
            Stripe portal session
        """
        logger.info("stripe_portal_create", customer_id=customer_id)

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return session

    async def _get_or_create_customer(self, user: User) -> str:
        """Get or create Stripe customer for user.

        Args:
            user: Application user

        Returns:
            Stripe customer ID
        """
        # TODO: Check if user already has a Stripe customer ID
        # For now, create a new customer
        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name or ''} {user.last_name or ''}".strip() or None,
            metadata={
                "user_id": str(user.id),
                "nip": user.nip,
            },
        )
        return customer.id

    async def construct_webhook_event(
        self,
        payload: bytes,
        sig_header: str | None,
    ) -> dict:
        """Construct and verify Stripe webhook event.

        Args:
            payload: Request body
            sig_header: Stripe-Signature header

        Returns:
            Stripe event dict
        """
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("Stripe webhook secret not configured")

        return stripe.Webhook.construct_event(
            payload, sig_header or "", settings.STRIPE_WEBHOOK_SECRET
        )

    async def handle_checkout_completed(
        self,
        session: dict,
        db: AsyncSession,
    ) -> None:
        """Handle checkout.session.completed webhook.

        Args:
            session: Stripe checkout session
            db: Database session
        """
        from sqlalchemy import select

        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        tier = metadata.get("tier")

        if not user_id or not tier:
            logger.warning("stripe_webhook_missing_metadata", session_id=session.get("id"))
            return

        logger.info("stripe_checkout_completed", user_id=user_id, tier=tier)

        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.error("stripe_user_not_found", user_id=user_id)
            return

        # Get subscription details
        stripe_subscription_id = session.get("subscription")
        customer_id = session.get("customer")

        # Create or update subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.tier = SubscriptionTier(tier)
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.stripe_subscription_id = stripe_subscription_id
            subscription.stripe_customer_id = customer_id
        else:
            subscription = Subscription(
                user_id=user_id,
                tier=SubscriptionTier(tier),
                status=SubscriptionStatus.ACTIVE,
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=customer_id,
            )
            db.add(subscription)

        await db.commit()

    async def handle_payment_succeeded(
        self,
        invoice: dict,
        db: AsyncSession,
    ) -> None:
        """Handle invoice.payment_succeeded webhook.

        Args:
            invoice: Stripe invoice
            db: Database session
        """
        logger.info("stripe_payment_succeeded", invoice_id=invoice.get("id"))
        # TODO: Update subscription period, send receipt email, etc.

    async def handle_subscription_cancelled(
        self,
        subscription: dict,
        db: AsyncSession,
    ) -> None:
        """Handle customer.subscription.deleted webhook.

        Args:
            subscription: Stripe subscription
            db: Database session
        """
        from sqlalchemy import select

        stripe_subscription_id = subscription.get("id")

        logger.info("stripe_subscription_cancelled", subscription_id=stripe_subscription_id)

        # Find and update subscription
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == stripe_subscription_id
            )
        )
        sub = result.scalar_one_or_none()

        if sub:
            sub.status = SubscriptionStatus.CANCELED
            await db.commit()
