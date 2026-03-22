"""
Payment Service - Complete subscription and payment logic with Stripe integration
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import stripe
from uuid import uuid4

from app.core.database import firebase_client
from app.core.config import settings
from app.models.payment import (
    Subscription, Invoice, PaymentMethod, Plan, SubscriptionStatus
)

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    """Payment service with complete business logic"""
    
    def __init__(self):
        self.plans = {
            "free": {
                "name": "Free",
                "price": 0,
                "features": [
                    "Basic questions",
                    "Limited practice sessions",
                    "Basic analytics"
                ],
                "limits": {
                    "questions_per_day": 20,
                    "practice_sessions": 5,
                    "resume_analyses": 1
                }
            },
            "pro": {
                "name": "Pro",
                "price": 19.99,
                "stripe_price_id": "price_pro_monthly",
                "features": [
                    "All questions",
                    "Unlimited practice",
                    "Advanced analytics",
                    "Company-specific grids",
                    "Resume analysis",
                    "Priority support"
                ],
                "limits": {
                    "questions_per_day": 999999,
                    "practice_sessions": 999999,
                    "resume_analyses": 999999
                }
            },
            "premium": {
                "name": "Premium",
                "price": 39.99,
                "stripe_price_id": "price_premium_monthly",
                "features": [
                    "Everything in Pro",
                    "AI Interviewer",
                    "Voice/video interviews",
                    "Personalized roadmap",
                    "Mock interviews",
                    "1-on-1 mentorship"
                ],
                "limits": {
                    "questions_per_day": 999999,
                    "practice_sessions": 999999,
                    "resume_analyses": 999999,
                    "ai_interviews": 999999
                }
            }
        }
    
    async def get_plans(self) -> List[Dict[str, Any]]:
        """Get available subscription plans"""
        
        plans = []
        for plan_id, plan in self.plans.items():
            plans.append({
                "plan_id": plan_id,
                "name": plan["name"],
                "price": plan["price"],
                "features": plan["features"],
                "limits": plan["limits"],
                "is_free": plan["price"] == 0
            })
        
        return plans
    
    async def create_subscription(
        self,
        user_id: str,
        price_id: str,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """Create a new subscription"""
        
        try:
            # Get or create Stripe customer
            customer = await self._get_or_create_customer(user_id)
            
            # Attach payment method
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer["id"]
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                customer["id"],
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            
            # Create subscription
            stripe_subscription = stripe.Subscription.create(
                customer=customer["id"],
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            
            # Determine plan from price_id
            plan_id = self._get_plan_id_from_price(price_id)
            
            # Create subscription record
            subscription_id = str(uuid4())
            subscription = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "stripe_subscription_id": stripe_subscription.id,
                "stripe_customer_id": customer["id"],
                "plan_id": plan_id,
                "status": self._map_stripe_status(stripe_subscription.status),
                "current_period_start": datetime.fromtimestamp(
                    stripe_subscription.current_period_start
                ).isoformat(),
                "current_period_end": datetime.fromtimestamp(
                    stripe_subscription.current_period_end
                ).isoformat(),
                "cancel_at_period_end": stripe_subscription.cancel_at_period_end,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            firebase_client.set_data(
                f"subscriptions/{user_id}/{subscription_id}",
                subscription
            )
            
            # Update user role
            firebase_client.update_data(f"users/{user_id}", {
                "role": plan_id,
                "subscription_id": subscription_id,
                "subscription_plan": plan_id,
                "subscription_expires": subscription["current_period_end"]
            })
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {str(e)}")
            raise ValueError(f"Payment failed: {str(e)}")
    
    async def _get_or_create_customer(self, user_id: str) -> Dict:
        """Get existing Stripe customer or create new one"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if not user:
            raise ValueError("User not found")
        
        # Check if user already has a Stripe customer ID
        stripe_customer_id = user.get("stripe_customer_id")
        if stripe_customer_id:
            try:
                customer = stripe.Customer.retrieve(stripe_customer_id)
                return customer
            except stripe.error.StripeError:
                pass
        
        # Create new customer
        customer = stripe.Customer.create(
            email=user["email"],
            name=user.get("display_name"),
            metadata={
                "user_id": user_id
            }
        )
        
        # Save customer ID
        firebase_client.update_data(f"users/{user_id}", {
            "stripe_customer_id": customer.id
        })
        
        return customer
    
    def _get_plan_id_from_price(self, price_id: str) -> str:
        """Get plan ID from Stripe price ID"""
        for plan_id, plan in self.plans.items():
            if plan.get("stripe_price_id") == price_id:
                return plan_id
        return "pro"  # Default
    
    def _map_stripe_status(self, stripe_status: str) -> str:
        """Map Stripe subscription status to internal status"""
        status_map = {
            "incomplete": "incomplete",
            "incomplete_expired": "incomplete_expired",
            "trialing": "trialing",
            "active": "active",
            "past_due": "past_due",
            "canceled": "canceled",
            "unpaid": "unpaid"
        }
        return status_map.get(stripe_status, "incomplete")
    
    async def get_current_subscription(self, user_id: str) -> Optional[Dict]:
        """Get user's current subscription"""
        
        subscriptions = firebase_client.get_data(f"subscriptions/{user_id}") or {}
        
        # Find active subscription
        for sub_id, sub in subscriptions.items():
            if sub.get("status") in ["active", "trialing"]:
                # Get plan details
                plan = self.plans.get(sub.get("plan_id"))
                if plan:
                    sub["plan_details"] = plan
                return sub
        
        return None
    
    async def update_subscription(
        self,
        user_id: str,
        subscription_id: str,
        price_id: str
    ) -> Dict:
        """Update subscription plan"""
        
        subscription = firebase_client.get_data(
            f"subscriptions/{user_id}/{subscription_id}"
        )
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        try:
            # Update in Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                items=[{
                    "id": stripe.Subscription.retrieve(
                        subscription["stripe_subscription_id"]
                    ).items.data[0].id,
                    "price": price_id
                }],
                proration_behavior="create_prorations"
            )
            
            # Update local record
            plan_id = self._get_plan_id_from_price(price_id)
            subscription["plan_id"] = plan_id
            subscription["updated_at"] = datetime.utcnow().isoformat()
            
            firebase_client.set_data(
                f"subscriptions/{user_id}/{subscription_id}",
                subscription
            )
            
            # Update user role
            firebase_client.update_data(f"users/{user_id}", {
                "role": plan_id,
                "subscription_plan": plan_id
            })
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error updating subscription: {str(e)}")
            raise ValueError(f"Update failed: {str(e)}")
    
    async def cancel_subscription(
        self,
        user_id: str,
        subscription_id: str,
        cancel_at_period_end: bool = True
    ) -> Dict:
        """Cancel subscription"""
        
        subscription = firebase_client.get_data(
            f"subscriptions/{user_id}/{subscription_id}"
        )
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        try:
            if cancel_at_period_end:
                # Cancel at period end
                stripe_subscription = stripe.Subscription.modify(
                    subscription["stripe_subscription_id"],
                    cancel_at_period_end=True
                )
                
                subscription["cancel_at_period_end"] = True
                subscription["status"] = "active"  # Still active until period end
                
            else:
                # Cancel immediately
                stripe_subscription = stripe.Subscription.delete(
                    subscription["stripe_subscription_id"]
                )
                subscription["status"] = "canceled"
            
            subscription["updated_at"] = datetime.utcnow().isoformat()
            
            firebase_client.set_data(
                f"subscriptions/{user_id}/{subscription_id}",
                subscription
            )
            
            # If canceled immediately, downgrade user
            if not cancel_at_period_end:
                firebase_client.update_data(f"users/{user_id}", {
                    "role": "free",
                    "subscription_plan": None
                })
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {str(e)}")
            raise ValueError(f"Cancel failed: {str(e)}")
    
    async def reactivate_subscription(self, user_id: str, subscription_id: str) -> Dict:
        """Reactivate canceled subscription"""
        
        subscription = firebase_client.get_data(
            f"subscriptions/{user_id}/{subscription_id}"
        )
        
        if not subscription:
            raise ValueError("Subscription not found")
        
        try:
            # Reactivate in Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription["stripe_subscription_id"],
                cancel_at_period_end=False
            )
            
            subscription["cancel_at_period_end"] = False
            subscription["status"] = "active"
            subscription["updated_at"] = datetime.utcnow().isoformat()
            
            firebase_client.set_data(
                f"subscriptions/{user_id}/{subscription_id}",
                subscription
            )
            
            # Update user role
            firebase_client.update_data(f"users/{user_id}", {
                "role": subscription["plan_id"],
                "subscription_plan": subscription["plan_id"]
            })
            
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error reactivating subscription: {str(e)}")
            raise ValueError(f"Reactivation failed: {str(e)}")
    
    async def get_payment_methods(self, user_id: str) -> List[Dict]:
        """Get user's payment methods"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if not user or not user.get("stripe_customer_id"):
            return []
        
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=user["stripe_customer_id"],
                type="card"
            )
            
            result = []
            for pm in payment_methods.data:
                result.append({
                    "id": pm.id,
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year,
                    "is_default": pm.id == user.get("default_payment_method")
                })
            
            return result
            
        except stripe.error.StripeError as e:
            logger.error(f"Error fetching payment methods: {str(e)}")
            return []
    
    async def add_payment_method(self, user_id: str, payment_method_id: str) -> Dict:
        """Add a payment method"""
        
        customer = await self._get_or_create_customer(user_id)
        
        try:
            # Attach payment method
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer["id"]
            )
            
            # If this is the first payment method, set as default
            existing_methods = await self.get_payment_methods(user_id)
            if not existing_methods:
                stripe.Customer.modify(
                    customer["id"],
                    invoice_settings={
                        "default_payment_method": payment_method_id
                    }
                )
                
                firebase_client.update_data(f"users/{user_id}", {
                    "default_payment_method": payment_method_id
                })
            
            return {
                "id": payment_method.id,
                "brand": payment_method.card.brand,
                "last4": payment_method.card.last4,
                "exp_month": payment_method.card.exp_month,
                "exp_year": payment_method.card.exp_year
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error adding payment method: {str(e)}")
            raise ValueError(f"Failed to add payment method: {str(e)}")
    
    async def remove_payment_method(self, user_id: str, payment_method_id: str):
        """Remove a payment method"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if not user:
            raise ValueError("User not found")
        
        try:
            # Detach from Stripe
            stripe.PaymentMethod.detach(payment_method_id)
            
            # If this was the default, clear it
            if user.get("default_payment_method") == payment_method_id:
                firebase_client.update_data(f"users/{user_id}", {
                    "default_payment_method": None
                })
                
        except stripe.error.StripeError as e:
            logger.error(f"Error removing payment method: {str(e)}")
            raise ValueError(f"Failed to remove payment method: {str(e)}")
    
    async def set_default_payment_method(self, user_id: str, payment_method_id: str):
        """Set default payment method"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if not user or not user.get("stripe_customer_id"):
            raise ValueError("User or customer not found")
        
        try:
            stripe.Customer.modify(
                user["stripe_customer_id"],
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            
            firebase_client.update_data(f"users/{user_id}", {
                "default_payment_method": payment_method_id
            })
            
        except stripe.error.StripeError as e:
            logger.error(f"Error setting default payment method: {str(e)}")
            raise ValueError(f"Failed to set default: {str(e)}")
    
    async def get_invoices(self, user_id: str, limit: int) -> List[Dict]:
        """Get user's invoices"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if not user or not user.get("stripe_customer_id"):
            return []
        
        try:
            invoices = stripe.Invoice.list(
                customer=user["stripe_customer_id"],
                limit=limit
            )
            
            result = []
            for invoice in invoices.data:
                result.append({
                    "id": invoice.id,
                    "number": invoice.number,
                    "amount": invoice.amount_paid / 100,
                    "currency": invoice.currency.upper(),
                    "status": invoice.status,
                    "pdf_url": invoice.invoice_pdf,
                    "created_at": datetime.fromtimestamp(
                        invoice.created
                    ).isoformat(),
                    "paid_at": datetime.fromtimestamp(
                        invoice.status_transitions.paid_at
                    ).isoformat() if invoice.status_transitions.paid_at else None
                })
            
            return result
            
        except stripe.error.StripeError as e:
            logger.error(f"Error fetching invoices: {str(e)}")
            return []
    
    async def get_invoice(self, user_id: str, invoice_id: str) -> Optional[Dict]:
        """Get invoice details"""
        
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            
            # Verify ownership
            user = firebase_client.get_data(f"users/{user_id}")
            if not user or invoice.customer != user.get("stripe_customer_id"):
                return None
            
            # Get line items
            items = []
            for item in invoice.lines.data:
                items.append({
                    "description": item.description,
                    "amount": item.amount / 100,
                    "quantity": item.quantity,
                    "period_start": datetime.fromtimestamp(
                        item.period.start
                    ).isoformat(),
                    "period_end": datetime.fromtimestamp(
                        item.period.end
                    ).isoformat()
                })
            
            return {
                "id": invoice.id,
                "number": invoice.number,
                "amount": invoice.amount_paid / 100,
                "currency": invoice.currency.upper(),
                "status": invoice.status,
                "pdf_url": invoice.invoice_pdf,
                "items": items,
                "created_at": datetime.fromtimestamp(invoice.created).isoformat(),
                "paid_at": datetime.fromtimestamp(
                    invoice.status_transitions.paid_at
                ).isoformat() if invoice.status_transitions.paid_at else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error fetching invoice: {str(e)}")
            return None
    
    async def handle_webhook(self, event: stripe.Event):
        """Handle Stripe webhook events"""
        
        event_type = event["type"]
        data = event["data"]["object"]
        
        logger.info(f"Processing Stripe webhook: {event_type}")
        
        if event_type == "invoice.payment_succeeded":
            await self._handle_payment_succeeded(data)
        elif event_type == "invoice.payment_failed":
            await self._handle_payment_failed(data)
        elif event_type == "customer.subscription.updated":
            await self._handle_subscription_updated(data)
        elif event_type == "customer.subscription.deleted":
            await self._handle_subscription_deleted(data)
    
    async def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        
        # Find subscription
        subscriptions = firebase_client.get_data("subscriptions") or {}
        for user_id, user_subs in subscriptions.items():
            for sub_id, sub in user_subs.items():
                if sub.get("stripe_subscription_id") == invoice.subscription:
                    # Update subscription status
                    sub["status"] = "active"
                    firebase_client.set_data(
                        f"subscriptions/{user_id}/{sub_id}",
                        sub
                    )
                    
                    # Create invoice record
                    invoice_id = str(uuid4())
                    firebase_client.set_data(
                        f"invoices/{user_id}/{invoice_id}",
                        {
                            "invoice_id": invoice_id,
                            "stripe_invoice_id": invoice.id,
                            "amount": invoice.amount_paid / 100,
                            "status": "paid",
                            "paid_at": datetime.utcnow().isoformat(),
                            "pdf_url": invoice.invoice_pdf
                        }
                    )
                    break
    
    async def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        
        # Find subscription
        subscriptions = firebase_client.get_data("subscriptions") or {}
        for user_id, user_subs in subscriptions.items():
            for sub_id, sub in user_subs.items():
                if sub.get("stripe_subscription_id") == invoice.subscription:
                    # Update subscription status
                    sub["status"] = "past_due"
                    firebase_client.set_data(
                        f"subscriptions/{user_id}/{sub_id}",
                        sub
                    )
                    
                    # Send notification to user
                    from app.services.notification_service import NotificationService
                    notification_service = NotificationService()
                    await notification_service.create_notification(
                        user_id,
                        "payment_failed",
                        {
                            "title": "Payment Failed",
                            "message": "Your latest payment failed. Please update your payment method."
                        }
                    )
                    break
    
    async def _handle_subscription_updated(self, subscription):
        """Handle subscription update"""
        
        # Find subscription
        subscriptions = firebase_client.get_data("subscriptions") or {}
        for user_id, user_subs in subscriptions.items():
            for sub_id, sub in user_subs.items():
                if sub.get("stripe_subscription_id") == subscription.id:
                    # Update subscription
                    sub["status"] = self._map_stripe_status(subscription.status)
                    sub["current_period_start"] = datetime.fromtimestamp(
                        subscription.current_period_start
                    ).isoformat()
                    sub["current_period_end"] = datetime.fromtimestamp(
                        subscription.current_period_end
                    ).isoformat()
                    sub["cancel_at_period_end"] = subscription.cancel_at_period_end
                    sub["updated_at"] = datetime.utcnow().isoformat()
                    
                    firebase_client.set_data(
                        f"subscriptions/{user_id}/{sub_id}",
                        sub
                    )
                    
                    # Update user role if needed
                    if subscription.status == "active":
                        firebase_client.update_data(f"users/{user_id}", {
                            "role": sub["plan_id"],
                            "subscription_plan": sub["plan_id"],
                            "subscription_expires": sub["current_period_end"]
                        })
                    break
    
    async def _handle_subscription_deleted(self, subscription):
        """Handle subscription deletion"""
        
        # Find subscription
        subscriptions = firebase_client.get_data("subscriptions") or {}
        for user_id, user_subs in subscriptions.items():
            for sub_id, sub in user_subs.items():
                if sub.get("stripe_subscription_id") == subscription.id:
                    # Update subscription
                    sub["status"] = "canceled"
                    sub["updated_at"] = datetime.utcnow().isoformat()
                    
                    firebase_client.set_data(
                        f"subscriptions/{user_id}/{sub_id}`",
                        sub
                    )
                    
                    # Downgrade user to free
                    firebase_client.update_data(f"users/{user_id}", {
                        "role": "free",
                        "subscription_plan": None,
                        "subscription_expires": None
                    })
                    break
    
    async def get_revenue_report(self, days: int) -> Dict[str, Any]:
        """Get revenue report (admin)"""
        
        try:
            # Get invoices from Stripe
            invoices = stripe.Invoice.list(
                status="paid",
                limit=100,
                created={
                    "gte": int((datetime.utcnow() - timedelta(days=days)).timestamp())
                }
            )
            
            total_revenue = 0
            daily_revenue = {}
            plan_revenue = {"free": 0, "pro": 0, "premium": 0}
            
            for invoice in invoices.data:
                amount = invoice.amount_paid / 100
                total_revenue += amount
                
                # Daily breakdown
                date = datetime.fromtimestamp(invoice.created).strftime("%Y-%m-%d")
                daily_revenue[date] = daily_revenue.get(date, 0) + amount
                
                # Plan breakdown
                for item in invoice.lines.data:
                    if "pro" in item.description.lower():
                        plan_revenue["pro"] += amount
                    elif "premium" in item.description.lower():
                        plan_revenue["premium"] += amount
            
            return {
                "total_revenue": total_revenue,
                "daily_revenue": daily_revenue,
                "plan_revenue": plan_revenue,
                "invoice_count": len(invoices.data),
                "average_revenue_per_day": total_revenue / days if days > 0 else 0
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error generating revenue report: {str(e)}")
            return {
                "total_revenue": 0,
                "daily_revenue": {},
                "plan_revenue": {},
                "invoice_count": 0,
                "average_revenue_per_day": 0
            }
    
    async def get_all_subscriptions(
        self,
        status: Optional[str],
        limit: int
    ) -> List[Dict]:
        """Get all subscriptions (admin)"""
        
        subscriptions = firebase_client.get_data("subscriptions") or {}
        
        result = []
        for user_id, user_subs in subscriptions.items():
            for sub_id, sub in user_subs.items():
                if status and sub.get("status") != status:
                    continue
                
                # Get user details
                user = firebase_client.get_data(f"users/{user_id}")
                
                result.append({
                    "subscription_id": sub_id,
                    "user_id": user_id,
                    "user_email": user.get("email") if user else "Unknown",
                    "user_name": user.get("display_name") if user else "Unknown",
                    "plan_id": sub.get("plan_id"),
                    "status": sub.get("status"),
                    "current_period_end": sub.get("current_period_end"),
                    "created_at": sub.get("created_at"),
                    "cancel_at_period_end": sub.get("cancel_at_period_end", False)
                })
        
        # Sort by created_at desc
        result.sort(key=lambda x: x["created_at"], reverse=True)
        
        return result[:limit]