from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    merchant = Column(String, index=True)
    location = Column(String)
    notes = Column(String, nullable=True)
    source = Column(String, default="MANUAL", index=True) # MANUAL, BANK_SYNC, RAZORPAY
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Fraud related fields
    fraud_score = Column(Float, nullable=True)
    is_suspicious = Column(Boolean, default=False)
    user_confirmed_safe = Column(Boolean, nullable=True) # None = Pending, True = Safe, False = Fraud

    user = relationship("User", backref="transactions")
