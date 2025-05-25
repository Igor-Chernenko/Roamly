from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database import get_gb, Base

#----------------------------------[ CREATE TEST USER DATABASE]----------------------------------
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOSTNAME}/{settings.DATABASE_NAME}_test"


engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind= engine
)

@pytest.fixture()
def session():
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS username_trgm_idx ON users USING gin (username gin_trgm_ops)"
        ))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS adventure_title_trgm_idx ON adventures USING gin (title gin_trgm_ops)"
        ))

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_gb():
        try:
            yield session
        finally:
            #session.close()
            pass
    app.dependency_overrides[get_gb] = override_get_gb
    yield TestClient(app)

    