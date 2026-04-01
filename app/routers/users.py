from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, require_admin
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserOut, UserUpdate
from app.services.user import delete_user, get_all_users, get_user_by_id, update_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=dict)
def list_users(
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users with optional filters. **Admin only.**"""
    skip = (page - 1) * page_size
    users, total = get_all_users(db, skip=skip, limit=page_size, role=role, is_active=is_active)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "items": [UserOut.model_validate(u) for u in users],
    }


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a user by ID.
    - Viewers/Analysts can only view their own profile.
    - Admins can view any profile.
    """
    if current_user.role != UserRole.admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view other users' profiles.",
        )
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user_profile(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update user details.
    - Users can update their own profile (but not their role).
    - Admins can update any user including role.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if current_user.role != UserRole.admin:
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update other users.")
        # Non-admins cannot change role or active status
        payload.role = None
        payload.is_active = None
    return update_user(db, user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a user and all their data. **Admin only.**"""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    delete_user(db, user)
