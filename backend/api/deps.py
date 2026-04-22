from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from core.config import settings
from core.database import get_db
from models.user import User
from models.advanced import BlacklistedToken

# Lightweight in-memory cache for faster blacklist rejection
_blacklist_cache = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if user_id is None:
            raise credentials_exception
            
        # Check blacklist cache first
        if jti in _blacklist_cache:
            raise HTTPException(status_code=401, detail="Token has been revoked/logged out")
            
        # Check blacklist DB
        if jti:
            blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token_jti == jti).first()
            if blacklisted:
                _blacklist_cache.add(jti)
                raise HTTPException(status_code=401, detail="Token has been revoked/logged out")
                
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
