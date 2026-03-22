"""
Payment Schemas - Pydantic models for payment and subscription
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Schemas
class CreateSubscriptionRequest(BaseModel):
    """Create subscription request"""
    price_id: str
    payment_method_id: str

# Response Schemas
class PlanResponse(BaseModel):
    """Plan response"""
    plan_id: str
    name: str
    price: float
    features: List[str] = Field(default_factory=list)
    limits: Dict[str, Any] = Field(default_factory=dict)
    is_free: bool = False
    
    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    """Subscription response"""
    subscription_id: str
    user_id: str
    plan_id: str
    status: str  # active, past_due, canceled, incomplete
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Optional fields
    plan_details: Optional[PlanResponse] = None
    
    class Config:
        from_attributes = True

class PaymentMethodResponse(BaseModel):
    """Payment method response"""
    id: str
    brand: str  # visa, mastercard, amex, etc.
    last4: str
    exp_month: int
    exp_year: int
    is_default: bool = False
    
    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: str
    number: Optional[str] = None
    amount: float
    currency: str = "usd"
    status: str  # paid, open, draft
    pdf_url: Optional[str] = None
    created_at: Optional[str] = None
    paid_at: Optional[str] = None
    items: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# Export all schemas
__all__ = [
    'CreateSubscriptionRequest',
    'PlanResponse',
    'SubscriptionResponse',
    'PaymentMethodResponse',
    'InvoiceResponse',
]