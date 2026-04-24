from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from core.database import engine, Base
from core.rate_limit import limiter
from api import auth, transactions, payments
from ws_manager.alerts import manager
from services.bank_sync import sync_bank_transactions

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models before creating tables
import models

# DB schema creation will happen in startup_event


app = FastAPI(title="NeuroShield API", description="AI-powered fraud detection banking app")

# CORS setup - Allowing all for portfolio simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Do not log stack trace in production response, just return a clean message
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An internal server error occurred."}
    )


scheduler = AsyncIOScheduler()

async def bank_sync_job():
    from services.bank_sync import sync_bank_transactions
    await sync_bank_transactions()

async def ml_retraining_job():
    from ml.retraining import run_retraining_job
    import asyncio
    # Run sync script in async safely
    await asyncio.to_thread(run_retraining_job)

async def token_cleanup_job():
    from core.database import SessionLocal
    from models.advanced import BlacklistedToken
    from datetime import datetime, timezone
    db = SessionLocal()
    try:
        db.query(BlacklistedToken).filter(BlacklistedToken.expires_at < datetime.now(timezone.utc)).delete()
        db.commit()
        print("Cleaned up expired tokens.")
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    from core.config import settings
    logger.info("Initializing database in background...")
    def init_db():
        from sqlalchemy import text
        try:
            Base.metadata.create_all(bind=engine)
            # Auto-migration for new Plaid columns if table already existed
            with engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN plaid_access_token VARCHAR"))
                except Exception: pass
                try:
                    conn.execute(text("ALTER TABLE users ADD COLUMN plaid_item_id VARCHAR"))
                except Exception: pass
                
                # FORCE RESET all balances to 0.0 to remove old mock data
                conn.execute(text("UPDATE users SET balance = 0.0"))
                conn.commit()
            logger.info("Database initialized and balances reset to 0.0.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
    
    # Run in background to prevent startup hang
    asyncio.create_task(asyncio.to_thread(init_db))

    logger.info("Initializing APScheduler jobs...")
    scheduler.add_job(bank_sync_job, 'interval', minutes=settings.SYNC_INTERVAL_MINUTES, id="bank_sync_internal", replace_existing=True, max_instances=1)
    scheduler.add_job(ml_retraining_job, 'interval', hours=settings.RETRAIN_INTERVAL_HOURS, id="ml_retrain_daily", replace_existing=True, max_instances=1) 
    scheduler.add_job(token_cleanup_job, 'interval', hours=1, id="token_cleanup_hourly", replace_existing=True, max_instances=1)  # Cleanup hourly
    scheduler.start()
    logger.info("Scheduler initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    logger.info("Scheduler shutdown.")

# Include Routers
# Need to apply limiter manually or globally to auth router
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(payments.router, prefix="/payment", tags=["Payments"])
from api import analytics, models_admin, bank
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(models_admin.router, prefix="/admin/models", tags=["Model Admin"])
app.include_router(bank.router, prefix="/bank", tags=["Bank Link"])

# WebSocket route for alerts
@app.websocket("/ws/alerts/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # We don't expect much client->server WS comms, just keeping it alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@app.get("/")
def root():
    return {"message": "Welcome to NeuroShield API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/test-db")
def test_db():
    from sqlalchemy import text
    from core.database import SessionLocal
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database connection works"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
