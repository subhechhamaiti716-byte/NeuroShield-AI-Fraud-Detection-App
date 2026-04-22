from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float
    category: str
    merchant: str
    location: Optional[str] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    source: Optional[str] = "MANUAL"

class TransactionOut(TransactionBase):
    id: int
    user_id: int
    source: str
    timestamp: datetime
    fraud_score: Optional[float]
    is_suspicious: bool
    risk_level: Optional[str] = "LOW"
    reasons: Optional[list] = []
    user_confirmed_safe: Optional[bool]

    class Config:
        from_attributes = True

class FraudFeedback(BaseModel):
    is_safe: bool
