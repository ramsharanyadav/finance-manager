import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "Finance Manager API is running"
    }

@router.get("/database")
def database_health(db: Session = Depends(get_db)):
    
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except SQLAlchemyError:

        logger.exception("Database health check failed")

        raise HTTPException(
            status_code= 503,
            detail="Database connection unavailable"
        )

         


