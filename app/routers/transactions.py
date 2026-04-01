from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, require_admin, require_analyst
from app.database import get_db
from app.models.transaction import Category, Transaction, TransactionType
from app.models.user import User, UserRole
from app.schemas.transaction import TransactionCreate, TransactionListResponse, TransactionOut, TransactionUpdate
from app.services.transaction import (
    create_transaction, delete_transaction,
    get_transaction_by_id, get_transactions,
    update_transaction,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _resolve_target_user_id(
    db: Session,
    current_user: User,
    target_user_id: Optional[int],
) -> Optional[int]:
    """
    Admins/Analysts can query all or a specific user's transactions.
    Viewers only see their own.
    """
    if current_user.role == UserRole.viewer:
        return current_user.id
    if target_user_id is not None:
        return target_user_id
    return None  # admin/analyst with no filter → all transactions


@router.get("/", response_model=TransactionListResponse)
def list_transactions(
    type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    category: Optional[Category] = Query(None, description="Filter by category"),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in description/notes"),
    user_id: Optional[int] = Query(None, description="Filter by user (admin/analyst only)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List transactions with filtering and pagination.
    - **Viewers** see only their own transactions.
    - **Analysts & Admins** can view all or filter by user.
    """
    target_uid = _resolve_target_user_id(db, current_user, user_id)
    return get_transactions(
        db,
        user_id=target_uid,
        type_filter=type,
        category_filter=category,
        date_from=date_from,
        date_to=date_to,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def add_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new financial transaction (any authenticated user)."""
    return create_transaction(db, payload, user_id=current_user.id)


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_single_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a single transaction by ID."""
    transaction = get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    if current_user.role == UserRole.viewer and transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionOut)
def edit_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update an existing transaction. Owners or admins can update."""
    transaction = get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    if transaction.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own transactions.",
        )
    return update_transaction(db, transaction, payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a transaction. Owner or Admin only."""
    transaction = get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found.")
    if transaction.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own transactions.",
        )
    delete_transaction(db, transaction)
