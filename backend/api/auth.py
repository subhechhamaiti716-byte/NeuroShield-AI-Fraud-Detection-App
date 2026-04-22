from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from core.config import settings
from models.user import User
from models.advanced import BlacklistedToken
from schemas.user import UserCreate, UserOut, Token, UserBase
from api.deps import get_current_user, oauth2_scheme

import logging

from core.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def signup(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Signup attempt for email: {user_in.email}")
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            logger.warning(f"Signup failed: Email already registered ({user_in.email})")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            phone=user_in.phone,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered successfully: {db_user.email}")
        return db_user
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Signup error for {user_in.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: Incorrect credentials for {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            subject=user.id, expires_delta=refresh_token_expires
        )
        
        user.hashed_refresh_token = get_password_hash(refresh_token)
        db.commit()

        logger.info(f"Login successful for user: {form_data.username}")
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Login error for {form_data.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

from pydantic import BaseModel
class RefreshTokenReq(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
def refresh_token(req: RefreshTokenReq, db: Session = Depends(get_db)):
    from jose import jwt, JWTError
    try:
        payload = jwt.decode(req.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.hashed_refresh_token or not verify_password(req.refresh_token, user.hashed_refresh_token):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    
    return {"access_token": new_access_token, "refresh_token": req.refresh_token, "token_type": "bearer"}

@router.post("/logout", status_code=200)
def logout(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    from jose import jwt
    try:
        # Decode the active access token and blacklist it
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            from datetime import datetime, timezone
            blacklist_entry = BlacklistedToken(
                token_jti=jti,
                user_id=current_user.id,
                expires_at=datetime.fromtimestamp(exp, tz=timezone.utc)
            )
            db.add(blacklist_entry)
            
        # Revoke the refresh token essentially
        current_user.hashed_refresh_token = None
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid token state for logout")
        
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
