from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token
from app.core.dependencies import get_current_active_user
from app.core.security import verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserOut, UserChangePassword
from app.services.user import (
    authenticate_user, create_user,
    get_user_by_email, get_user_by_username, change_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    if get_user_by_username(db, payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{payload.username}' is already taken.",
        )
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' is already registered.",
        )
    user = create_user(db, payload)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Obtain a JWT access token using username + password."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=expire_minutes),
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expire_minutes * 60,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.put("/me/password", status_code=status.HTTP_200_OK)
def update_my_password(
    payload: UserChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change current user's password."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )
    change_password(db, current_user, payload.new_password)
    return {"message": "Password updated successfully."}
