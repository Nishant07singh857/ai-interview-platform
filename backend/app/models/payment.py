"""
Payment Models - Payment and subscription models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SubscriptionStatus(str, Enum):
    """Subscription status enum"""
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"

class Plan(BaseModel):
    """Subscription plan model"""
    plan_id: str
    name: str
    description: Optional[str] = None
    price: float
    currency: str = "usd"
    interval: str = "month"  # month, year
    features: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    stripe_price_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Subscription(BaseModel):
    """Subscription model"""
    subscription_id: str
    user_id: str
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    plan_id: str
    status: SubscriptionStatus
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Invoice(BaseModel):
    """Invoice model"""
    invoice_id: str
    user_id: str
    stripe_invoice_id: str
    subscription_id: Optional[str] = None
    amount: float
    currency: str = "usd"
    status: str  # draft, open, paid, void
    pdf_url: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaymentMethod(BaseModel):
    """Payment method model"""
    payment_method_id: str
    user_id: str
    stripe_payment_method_id: str
    type: str = "card"  # card, bank_account, etc.
    brand: Optional[str] = None  # visa, mastercard, etc.
    last4: Optional[str] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Export all models
__all__ = [
    'SubscriptionStatus',
    'Plan',
    'Subscription',
    'Invoice',
    'PaymentMethod'
]