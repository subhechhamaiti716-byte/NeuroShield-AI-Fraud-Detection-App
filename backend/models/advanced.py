from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class FraudLog(Base):
    __tablename__ = "fraud_logs"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False) # LOW, MEDIUM, HIGH
    reasons = Column(JSON, nullable=False) # e.g. ["Unusual amount", "New location"]
    user_feedback_is_safe = Column(Boolean, nullable=True) # Used for feedback loop
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", backref="fraud_logs")
    user = relationship("User", backref="fraud_logs")

class UserBehaviorProfile(Base):
    __tablename__ = "user_behavior_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    avg_spending = Column(Float, default=0.0)
    std_spending = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    frequent_locations = Column(JSON, default=list) # List of frequent location strings/coords
    frequent_categories = Column(JSON, default=dict) # Count of categories
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", backref="behavior_profile", uselist=False)

class PaymentLog(Base):
    __tablename__ = "payment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True, index=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    payment_id = Column(String, unique=True, index=True, nullable=True)
    signature = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String, default="CREATED", index=True) # CREATED, CAPTURED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="payment_logs")
    transaction = relationship("Transaction", backref="payment_logs")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True, nullable=False)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    path = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BlacklistedToken(Base):
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), index=True, nullable=False)
