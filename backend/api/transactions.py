from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.transaction import Transaction
from models.user import User
from models.advanced import FraudLog, UserBehaviorProfile
from schemas.transaction import TransactionCreate, TransactionOut, FraudFeedback
from api.deps import get_current_user
from ml.fraud_model import fraud_model
from websockets.alerts import manager

router = APIRouter()

def get_or_create_profile(user_id: int, db: Session):
    profile = db.query(UserBehaviorProfile).filter(UserBehaviorProfile.user_id == user_id).first()
    if not profile:
        profile = UserBehaviorProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.post("/add", response_model=TransactionOut)
async def add_transaction(
    tx_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check balance
    if current_user.balance < tx_in.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Get user profile for feature engineering
    profile = get_or_create_profile(current_user.id, db)

    # Run advanced fraud detection
    ml_result = fraud_model.evaluate(tx_in.model_dump(), profile)

    # Save transaction to DB
    db_tx = Transaction(
        user_id=current_user.id,
        amount=tx_in.amount,
        category=tx_in.category,
        merchant=tx_in.merchant,
        location=tx_in.location,
        notes=tx_in.notes,
        source=tx_in.source,
        fraud_score=ml_result["risk_score"],
        is_suspicious=ml_result["is_suspicious"]
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)

    # If suspicious, log to FraudLogs
    if ml_result["is_suspicious"]:
        fraud_log = FraudLog(
            transaction_id=db_tx.id,
            user_id=current_user.id,
            risk_score=ml_result["risk_score"],
            risk_level=ml_result["risk_level"],
            reasons=ml_result["reasons"]
        )
        db.add(fraud_log)
    else:
        # Update user profile if normal (Simple Online Update)
        profile.avg_spending = ((profile.avg_spending * profile.transaction_count) + tx_in.amount) / (profile.transaction_count + 1)
        profile.transaction_count += 1
        current_user.balance -= tx_in.amount
        
    db.commit()

    # Create response with the correct schema
    response_data = db_tx.__dict__.copy()
    response_data["risk_level"] = ml_result["risk_level"]
    response_data["reasons"] = ml_result["reasons"]

    # Trigger WebSocket alert if suspicious
    if ml_result["is_suspicious"]:
        await manager.send_alert(
            user_id=str(current_user.id),
            message={
                "type": "FRAUD_ALERT",
                "transaction_id": db_tx.id,
                "amount": db_tx.amount,
                "merchant": db_tx.merchant,
                "risk_level": ml_result["risk_level"],
                "reasons": ml_result["reasons"],
                "message": "Suspicious transaction detected!"
            }
        )

    return response_data

@router.get("/", response_model=List[TransactionOut])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Map fraud logs conceptually if needed
    results = []
    for tx in transactions:
        tx_data = tx.__dict__.copy()
        fraud_log = db.query(FraudLog).filter(FraudLog.transaction_id == tx.id).first()
        if fraud_log:
            tx_data["risk_level"] = fraud_log.risk_level
            tx_data["reasons"] = fraud_log.reasons
        else:
            tx_data["risk_level"] = "LOW"
            tx_data["reasons"] = []
        results.append(tx_data)
        
    return results

@router.put("/{tx_id}/feedback", response_model=TransactionOut)
def provide_feedback(
    tx_id: int,
    feedback: FraudFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    tx.user_confirmed_safe = feedback.is_safe
    
    fraud_log = db.query(FraudLog).filter(FraudLog.transaction_id == tx_id).first()
    if fraud_log:
        fraud_log.user_feedback_is_safe = feedback.is_safe
    
    if tx.is_suspicious and feedback.is_safe:
        if current_user.balance >= tx.amount:
            current_user.balance -= tx.amount
        else:
            raise HTTPException(status_code=400, detail="Insufficient funds to process safe transaction")
            
    db.commit()
    
    tx_data = tx.__dict__.copy()
    if fraud_log:
        tx_data["risk_level"] = fraud_log.risk_level
        tx_data["reasons"] = fraud_log.reasons
    else:
        tx_data["risk_level"] = "LOW"
        tx_data["reasons"] = []
        
    return tx_data
