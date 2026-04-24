import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NeuroShield API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-jwt-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # Shorter access token for security
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # Refresh token duration
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./neuroshield.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8081,http://localhost:3000,http://localhost:19006,*")

    # Razorpay
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_mockkeyid123")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "mocksecretkey456")

    # Scheduler
    SYNC_INTERVAL_MINUTES: int = int(os.getenv("SYNC_INTERVAL_MINUTES", "5"))
    RETRAIN_INTERVAL_HOURS: int = int(os.getenv("RETRAIN_INTERVAL_HOURS", "24"))

    # Plaid
    PLAID_CLIENT_ID: str = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET: str = os.getenv("PLAID_SECRET", "")
    PLAID_ENV: str = os.getenv("PLAID_ENV", "sandbox")
    PLAID_PRODUCTS: str = os.getenv("PLAID_PRODUCTS", "auth,transactions,balance")
    PLAID_COUNTRY_CODES: str = os.getenv("PLAID_COUNTRY_CODES", "US,IN")

    class Config:
        env_file = ".env"

settings = Settings()
