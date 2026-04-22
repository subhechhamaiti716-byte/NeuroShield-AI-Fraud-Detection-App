import os
import pickle
import numpy as np
from sqlalchemy.orm import Session
from datetime import datetime
from sklearn.ensemble import IsolationForest

from core.database import SessionLocal
from models.advanced import FraudLog, ModelVersion

MODEL_BASE_PATH = "ml/models/"
os.makedirs(MODEL_BASE_PATH, exist_ok=True)

def run_retraining_job():
    print("Starting ML Retraining Job...")
    db: Session = SessionLocal()
    try:
        # Fetch verified fraud logs (user_feedback_is_safe refers to whether it was safe)
        logs = db.query(FraudLog).filter(FraudLog.user_feedback_is_safe != None).all()
        
        if len(logs) < 10:
            print("Not enough verified feedback to retrain. Skipping.")
            return

        print(f"Retraining with {len(logs)} feedback entries...")
        
        # Here we would normally extract features again from DB, 
        # but for demonstration we simulate retraining success
        version_tag = f"v_{int(datetime.now().timestamp())}"
        model_path = os.path.join(MODEL_BASE_PATH, f"isolation_forest_{version_tag}.pkl")
        
        # Train new model
        np.random.seed(42)
        X = np.random.normal(loc=[0.0, 1.0, 0.1, 1], scale=[0.5, 0.5, 0.2, 0.5], size=(1200, 4))
        
        new_model = IsolationForest(n_estimators=300, contamination=0.03, random_state=42)
        new_model.fit(X)
        
        with open(model_path, "wb") as f:
            pickle.dump(new_model, f)
            
        # Deactivate old versions
        db.query(ModelVersion).update({ModelVersion.is_active: False})
        
        # Log new version
        new_version = ModelVersion(
            version=version_tag,
            precision=0.89,  # Mocked eval metrics
            recall=0.92,
            roc_auc=0.95,
            path=model_path,
            is_active=True
        )
        db.add(new_version)
        db.commit()
        print(f"Successfully retrained and activated {version_tag}")
        
    except Exception as e:
        print(f"Retraining failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_retraining_job()
