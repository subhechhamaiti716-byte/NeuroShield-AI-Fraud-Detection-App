import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

# Import SessionLocal carefully to avoid circular loops
from core.database import SessionLocal
from models.advanced import ModelVersion

MODEL_FALLBACK_PATH = "ml/models/isolation_forest_fallback.pkl"

class AdvancedFraudDetectionModel:
    def __init__(self):
        self.model = None
        self.current_version = None
        self._reload_model()

    def _train_dummy_model(self):
        np.random.seed(42)
        normal_data = np.random.normal(loc=[0.0, 1.0, 0.1, 1], scale=[0.5, 0.5, 0.2, 0.5], size=(1000, 4))
        anomalies = np.random.normal(loc=[5.0, 5.0, 0.9, 5], scale=[1.0, 1.0, 0.1, 1.0], size=(50, 4))
        
        X = np.vstack([normal_data, anomalies])
        
        self.model = IsolationForest(n_estimators=200, contamination=0.03, random_state=42)
        self.model.fit(X)
        
        os.makedirs(os.path.dirname(MODEL_FALLBACK_PATH), exist_ok=True)
        with open(MODEL_FALLBACK_PATH, "wb") as f:
            pickle.dump(self.model, f)
            
        return MODEL_FALLBACK_PATH

    def _reload_model(self):
        db: Session = SessionLocal()
        try:
            active_version_entry = db.query(ModelVersion).filter(ModelVersion.is_active == True).order_by(ModelVersion.created_at.desc()).first()
            if active_version_entry and os.path.exists(active_version_entry.path):
                with open(active_version_entry.path, "rb") as f:
                    self.model = pickle.load(f)
                self.current_version = active_version_entry.version
            else:
                # No DB active version found, fallback or train
                if os.path.exists(MODEL_FALLBACK_PATH):
                    with open(MODEL_FALLBACK_PATH, "rb") as f:
                        self.model = pickle.load(f)
                else:
                    self._train_dummy_model()
                self.current_version = "fallback"
        except Exception as e:
            print(f"Error loading model: {e}")
            if not self.model: # Absolute basic fallback if completely failed
                if os.path.exists(MODEL_FALLBACK_PATH):
                    with open(MODEL_FALLBACK_PATH, "rb") as f:
                        self.model = pickle.load(f)
                else:
                    self._train_dummy_model()
        finally:
            db.close()

    def evaluate(self, transaction: dict, user_profile) -> dict:
        """
        Evaluate risk using hybrid approach (ML + Rules)
        """
        amount = transaction.get("amount", 0)
        category = transaction.get("category", "")
        
        # 1. Feature Engineering
        amount_deviation = 0.0
        if user_profile and user_profile.avg_spending > 0:
            amount_deviation = (amount - user_profile.avg_spending) / (user_profile.std_spending or 1.0)
            
        frequency_factor = 1.0 
        
        hour = datetime.now().hour
        time_anomaly = 1.0 if (hour >= 1 and hour <= 5) else 0.1
        
        category_map = {"Shopping": 1, "Food": 2, "Travel": 3, "Transfer": 4, "Bills": 5}
        cat_encoded = category_map.get(category, 0)
        
        # ML Evaluation
        X = np.array([[amount_deviation, frequency_factor, time_anomaly, cat_encoded]])
        if self.model:
            score_sample = self.model.score_samples(X)[0]
            ml_risk_score = min(max(-score_sample * 0.8, 0), 1.0)
        else:
            ml_risk_score = 0.0
        
        # 2. Rule-based Evaluation (Overrides)
        reasons = []
        rule_risk_score = 0.0
        
        if amount_deviation > 3.0:
            reasons.append("Highly unusual amount deviation")
            rule_risk_score = max(rule_risk_score, 0.8)
            
        if time_anomaly > 0.8:
            reasons.append("Unusual night-time transaction")
            rule_risk_score = max(rule_risk_score, 0.6)
            
        final_score = max(ml_risk_score, rule_risk_score)
        
        if final_score > 0.75:
            risk_level = "HIGH"
        elif final_score > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        if final_score > 0.75 and not reasons:
            reasons.append("AI Pattern Anomaly detected")
            
        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "is_suspicious": final_score > 0.75,
            "reasons": reasons,
            "model_version": self.current_version
        }

fraud_model = AdvancedFraudDetectionModel()
