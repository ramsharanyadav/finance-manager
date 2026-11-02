from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Personal Finance Management REST API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Register API routes
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)

@app.get("/")
def root():
    return {
        "message": "Welcome to Finance Manager API",
        "version": settings.APP_VERSION
    }