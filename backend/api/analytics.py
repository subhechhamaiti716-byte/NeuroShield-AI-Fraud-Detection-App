from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta

from core.database import get_db
from models.user import User
from models.transaction import Transaction
from models.advanced import FraudLog, ModelVersion, UserBehaviorProfile
from api.deps import get_current_user

router = APIRouter()

@router.get("/summary")
def get_analytics_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    seven_days_ago = datetime.now() - timedelta(days=7)
    fourteen_days_ago = datetime.now() - timedelta(days=14)
    
    current_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.timestamp >= seven_days_ago
    ).scalar() or 0.0

    previous_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.timestamp >= fourteen_days_ago,
        Transaction.timestamp < seven_days_ago
    ).scalar() or 0.0

    # Category breakdown (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    category_data = db.query(Transaction.category, func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.timestamp >= thirty_days_ago
    ).group_by(Transaction.category).all()
    
    categories = [{"name": c[0], "amount": c[1]} for c in category_data]
    
    # Fraud Stats (All time)
    fraud_stats = db.query(FraudLog.risk_level, func.count(FraudLog.id)).filter(
        FraudLog.user_id == current_user.id
    ).group_by(FraudLog.risk_level).all()
    
    frauds = [{"level": f[0], "count": f[1]} for f in fraud_stats]
    
    # Fraud Trends Over Time (Last 14 days)
    fraud_trend = db.query(cast(FraudLog.created_at, Date).label("date"), func.count(FraudLog.id)).filter(
        FraudLog.user_id == current_user.id,
        FraudLog.created_at >= fourteen_days_ago
    ).group_by(cast(FraudLog.created_at, Date)).order_by("date").all()
    
    trends = [{"date": str(t[0]), "incidents": t[1]} for t in fraud_trend]
    
    # Behavior Profile context
    profile = db.query(UserBehaviorProfile).filter(UserBehaviorProfile.user_id == current_user.id).first()
    avg_spend = profile.avg_spending if profile else 0.0

    return {
        "current_spent": current_spent,
        "previous_spent": previous_spent,
        "spending_change_pct": ((current_spent - previous_spent) / (previous_spent or 1.0)) * 100,
        "categories": categories,
        "frauds": frauds,
        "fraud_trends": trends,
        "average_spending": avg_spend
    }

@router.get("/model-performance")
def get_model_metrics(db: Session = Depends(get_db)):
    # Returns global ML model performance metrics natively
    active_model = db.query(ModelVersion).filter(ModelVersion.is_active == True).order_by(ModelVersion.created_at.desc()).first()
    if active_model:
        return {
            "version": active_model.version,
            "precision": active_model.precision or "Evaluating...",
            "recall": active_model.recall or "Evaluating...",
            "roc_auc": active_model.roc_auc or "Evaluating..."
        }
    return {"message": "No active models loaded into the DB layer"}

@router.get("/top-fraud-reasons")
def get_top_fraud_reasons(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Aggregates reasons over user history extracting elements from JSON
    fraud_logs = db.query(FraudLog.reasons).filter(FraudLog.user_id == current_user.id).all()
    
    reason_counts = {}
    for log in fraud_logs:
        reasons_list = log[0]
        if isinstance(reasons_list, list):
            for r in reasons_list:
                reason_counts[r] = reason_counts.get(r, 0) + 1
                
    sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"reason": item[0], "count": item[1]} for item in sorted_reasons]
