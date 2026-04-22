from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from core.database import engine, Base
from api import auth, transactions, payments
from websockets.alerts import manager
from services.bank_sync import sync_bank_transactions

limiter = Limiter(key_func=get_remote_address)

# Create DB schema
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NeuroShield API", description="AI-powered fraud detection banking app")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Since mobile apps usually need permissive CORS locally, or we set exact app schemas.
    allow_credentials=True,
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

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    from core.config import settings
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
from api import analytics, models_admin
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(models_admin.router, prefix="/admin/models", tags=["Model Admin"])

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
