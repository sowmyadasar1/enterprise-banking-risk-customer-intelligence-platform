"""Customer API schemas."""
from pydantic import BaseModel
from typing import Optional

class CustomerResponse(BaseModel):
    """Schema for customer details response."""
    id: str
    name: str
    segment: str

class CustomerRiskProfile(BaseModel):
    """Schema for customer risk profile response."""
    customer_id: str
    risk_score: float
    risk_category: str
