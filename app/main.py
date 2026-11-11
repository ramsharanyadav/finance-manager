from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Personal Finance Management REST API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "default",
            "description": "Root API Route",
        },
        {
            "name": "Health",
            "description": "Health and database health",
        },
        {
            "name": "Authentication",
            "description": "Registration, login, token refresh, logout and password management.",
        },
        {
            "name": "Users",
            "description": "User profile and account management.",
        },
        {
            "name": "Accounts",
            "description": "Manage personal financial accounts.",
        },
        {
            "name": "Categories",
            "description": "Manage income and expense categories.",
        },
        {
            "name": "Transactions",
            "description": "Create, view, update and delete financial transactions.",
        },
        {
            "name": "Budgets",
            "description": "Manage monthly and category-based budgets.",
        },
        {
            "name": "Reports",
            "description": "Financial summaries and reports.",
        },
    ],
)

@app.exception_handler(AppException)
async def application_exception_handler(
    request: Request,
    exc: AppException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
        },
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