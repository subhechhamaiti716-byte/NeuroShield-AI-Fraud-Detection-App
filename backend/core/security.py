from datetime import datetime, timedelta, timezone
from typing import Any, Union
import bcrypt
import hashlib
from jose import jwt
import uuid
from core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate to 72 characters to prevent bcrypt 72 byte limit error
    password_bytes = plain_password[:72].encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    # Truncate to 72 characters to prevent bcrypt 72 byte limit error
    password_bytes = password[:72].encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def hash_token(token: str) -> str:
    """Hash a long token (like refresh JWT) using SHA-256 since bcrypt has 72-byte limit."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def verify_token_hash(token: str, hashed: str) -> bool:
    """Verify a token against its SHA-256 hash."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest() == hashed

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject), "type": "access", "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh", "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
