from typing import Optional
import re
from pydantic import BaseModel, EmailStr, field_validator

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if v is not None:
            if not re.fullmatch(r'\d{10}', v):
                raise ValueError('Phone number must be exactly 10 digits')
        return v



class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least 1 uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least 1 lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least 1 number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least 1 special character')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    balance: float
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
