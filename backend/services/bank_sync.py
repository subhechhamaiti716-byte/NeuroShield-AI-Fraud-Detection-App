import asyncio
import random
from sqlalchemy.orm import Session
from datetime import datetime

from core.database import SessionLocal
from models.user import User
from models.transaction import Transaction
from ml.fraud_model import fraud_model
from api.transactions import get_or_create_profile
from ws_manager.alerts import manager

MERCHANTS = ["Amazon", "Uber", "Starbucks", "Netflix", "Shell", "Target"]
CATEGORIES = ["Shopping", "Travel", "Food", "Bills", "Auto", "Shopping"]

async def sync_bank_transactions():
    """
    Simulates a background process pulling data from a Bank API (e.g. Plaid)
    """
    print("Running Bank Sync...")
    db: Session = SessionLocal()
    try:
        # Fetch all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            # 1. Simulate fixed subscription firing on some days
            day_of_month = datetime.now().day
            if random.random() < 0.05: # 5% chance of subscription hook hitting today
                subs = [("Netflix", 15.99, "Bills"), ("Spotify", 9.99, "Bills"), ("Gym", 45.0, "Shopping")]
                sub_merchant, sub_amount, sub_cat = random.choice(subs)
                db_tx = Transaction(
                    user_id=user.id,
                    amount=sub_amount,
                    category=sub_cat,
                    merchant=sub_merchant,
                    location="Auto Synced",
                    notes="Recurring Subscription",
                    source="BANK_SYNC",
                    fraud_score=0.1,
                    is_suspicious=False
                )
                user.balance -= sub_amount
                db.add(db_tx)
                db.commit()
                db.refresh(db_tx)
                continue
                
            # 2. Standard 10% chance per run to generate a varying transaction
            if random.random() < 0.1:
                amount = round(random.uniform(5.0, 150.0), 2)
                idx = random.randint(0, len(MERCHANTS) - 1)
                
                profile = get_or_create_profile(user.id, db)
                
                # Formulate dict to run through ML silently
                tx_dict = {
                    "amount": amount,
                    "category": CATEGORIES[idx],
                    "merchant": MERCHANTS[idx],
                    "timestamp": datetime.now()
                }
                
                ml_result = fraud_model.evaluate(tx_dict, profile)
                
                # Mock Bank pushing transaction directly without API
                db_tx = Transaction(
                    user_id=user.id,
                    amount=amount,
                    category=CATEGORIES[idx],
                    merchant=MERCHANTS[idx],
                    location="Auto Synced",
                    notes="Bank Sync",
                    source="BANK_SYNC",
                    fraud_score=ml_result["risk_score"],
                    is_suspicious=ml_result["is_suspicious"]
                )
                
                if not ml_result["is_suspicious"]:
                    user.balance -= amount
                    
                db.add(db_tx)
                db.commit()
                db.refresh(db_tx)
                
                # Push real-time WS notification about the new sync specifically
                if ml_result["is_suspicious"]:
                    await manager.send_alert(
                        user_id=str(user.id),
                        message={
                            "type": "FRAUD_ALERT",
                            "transaction_id": db_tx.id,
                            "amount": db_tx.amount,
                            "merchant": db_tx.merchant,
                            "risk_level": ml_result["risk_level"],
                            "message": "Suspicious Bank Sync detected!"
                        }
                    )
                else:
                    await manager.send_alert(
                        user_id=str(user.id),
                        message={
                            "type": "BANK_SYNC",
                            "message": f"New transaction from {db_tx.merchant} synced."
                        }
                    )
    except Exception as e:
        print(f"Bank Sync Error: {e}")
    finally:
        db.close()
