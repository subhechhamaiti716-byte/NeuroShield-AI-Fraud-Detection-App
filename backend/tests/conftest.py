import pytest
from sqlalchemy import create_url
from sqlalchemy.orm import sessionmaker
from core.database import Base, engine, SessionLocal
from main import app
from fastapi.testclient import TestClient

# Mock database url for testing (SQLite in-memory or a separate test DB)
# For simplicity in this demo, we'll use the current engine but we should ideally use a test DB
@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
