from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.advanced import ModelVersion
from models.user import User
from api.deps import get_current_user
from ml.fraud_model import fraud_model

router = APIRouter()

# Simple dependency placeholder for Admin check
def get_admin_user(current_user: User = Depends(get_current_user)):
    # In production, check if current_user has 'is_admin' or role
    return current_user

@router.get("/versions")
def list_versions(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    versions = db.query(ModelVersion).order_by(ModelVersion.created_at.desc()).all()
    return versions

@router.post("/rollback/{version_id}")
def rollback_model(version_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
        
    import os
    if not os.path.exists(version.path):
        raise HTTPException(status_code=400, detail="Model file does not exist on disk")

    # Deactivate all active versions
    db.query(ModelVersion).update({ModelVersion.is_active: False})
    
    # Activate selected
    version.is_active = True
    db.commit()
    
    # Trigger reload in memory
    fraud_model._reload_model()
    
    return {"status": f"Rolled back to version {version.version}", "current_active_version": fraud_model.current_version}
