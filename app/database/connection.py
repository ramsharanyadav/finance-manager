from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create PostgreSQL connection URL safely
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Create database session factory
SessionLocal = sessionmaker(
    bind= engine,
    autoflush=False,
    expire_on_commit=False,
)

# Database dependency
def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()