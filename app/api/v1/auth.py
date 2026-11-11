
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    ChangePasswordRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# --------------------------------------------------
# Register
# --------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    return AuthService.register_user(db, data)


# --------------------------------------------------
# Login
# --------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    return AuthService.login_user(db, data)


# --------------------------------------------------
# Refresh Token
# --------------------------------------------------

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    return AuthService.refresh_tokens(
        db,
        data.refresh_token,
    )


# --------------------------------------------------
# Logout
# --------------------------------------------------

@router.post("/logout")
def logout(
    data: LogoutRequest,
    db: Session = Depends(get_db),
):
    AuthService.logout_user(
        db,
        data.refresh_token,
    )

    return {
        "success": True,
        "message": "Logged out successfully",
    }


# --------------------------------------------------
# Current User
# --------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user=Depends(get_current_user),
):
    return current_user


# --------------------------------------------------
# Change Password
# --------------------------------------------------

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService.change_password(
        db,
        current_user,
        data,
    )

    return {
        "success": True,
        "message": "Password changed successfully. Please log in again.",
    }
