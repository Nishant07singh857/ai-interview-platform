"""
Payments Endpoints - Complete subscription and payment API
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional
import logging
import stripe

from app.core.deps import get_current_user, get_current_admin_user, get_current_user_optional, get_current_pro_user
from app.models.user import User
from app.schemas.payment import (
    PlanResponse, SubscriptionResponse, PaymentMethodResponse,
    InvoiceResponse, CreateSubscriptionRequest
)
from app.services.payment_service import PaymentService
from app.core.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])
logger = logging.getLogger(__name__)
payment_service = PaymentService()

# Stripe webhook (no auth)
@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        await payment_service.handle_webhook(event)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Plans
@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Get available subscription plans"""
    try:
        plans = await payment_service.get_plans()
        return plans
    except Exception as e:
        logger.error(f"Error getting plans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get plans")

# Subscriptions
@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new subscription"""
    try:
        subscription = await payment_service.create_subscription(
            current_user.uid,
            subscription_data.price_id,
            subscription_data.payment_method_id
        )
        return subscription
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")

@router.get("/subscriptions/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription"""
    try:
        subscription = await payment_service.get_current_subscription(current_user.uid)
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription")
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subscription")

@router.put("/subscriptions/{subscription_id}")
async def update_subscription(
    subscription_id: str,
    price_id: str,
    current_user: User = Depends(get_current_user)
):
    """Update subscription plan"""
    try:
        subscription = await payment_service.update_subscription(
            current_user.uid,
            subscription_id,
            price_id
        )
        return subscription
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update subscription")

@router.post("/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel subscription"""
    try:
        result = await payment_service.cancel_subscription(
            current_user.uid,
            subscription_id
        )
        return result
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

@router.post("/subscriptions/{subscription_id}/reactivate")
async def reactivate_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_user)
):
    """Reactivate canceled subscription"""
    try:
        result = await payment_service.reactivate_subscription(
            current_user.uid,
            subscription_id
        )
        return result
    except Exception as e:
        logger.error(f"Error reactivating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reactivate subscription")

# Payment Methods
@router.get("/methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_user)
):
    """Get user's payment methods"""
    try:
        methods = await payment_service.get_payment_methods(current_user.uid)
        return methods
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get payment methods")

@router.post("/methods", response_model=PaymentMethodResponse)
async def add_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """Add a payment method"""
    try:
        method = await payment_service.add_payment_method(
            current_user.uid,
            payment_method_id
        )
        return method
    except Exception as e:
        logger.error(f"Error adding payment method: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add payment method")

@router.delete("/methods/{payment_method_id}")
async def remove_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a payment method"""
    try:
        await payment_service.remove_payment_method(
            current_user.uid,
            payment_method_id
        )
        return {"message": "Payment method removed successfully"}
    except Exception as e:
        logger.error(f"Error removing payment method: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove payment method")

@router.put("/methods/default")
async def set_default_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """Set default payment method"""
    try:
        await payment_service.set_default_payment_method(
            current_user.uid,
            payment_method_id
        )
        return {"message": "Default payment method updated"}
    except Exception as e:
        logger.error(f"Error setting default payment method: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to set default payment method")

# Invoices
@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get user's invoices"""
    try:
        invoices = await payment_service.get_invoices(current_user.uid, limit)
        return invoices
    except Exception as e:
        logger.error(f"Error getting invoices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get invoices")

@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get invoice details"""
    try:
        invoice = await payment_service.get_invoice(current_user.uid, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get invoice")

# Admin endpoints
@router.get("/admin/revenue")
async def get_revenue_report(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(get_current_admin_user)
):
    """Get revenue report (admin only)"""
    try:
        report = await payment_service.get_revenue_report(days)
        return report
    except Exception as e:
        logger.error(f"Error getting revenue report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get revenue report")

@router.get("/admin/subscriptions")
async def get_all_subscriptions(
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    admin: User = Depends(get_current_admin_user)
):
    """Get all subscriptions (admin only)"""
    try:
        subscriptions = await payment_service.get_all_subscriptions(status, limit)
        return subscriptions
    except Exception as e:
        logger.error(f"Error getting subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subscriptions")