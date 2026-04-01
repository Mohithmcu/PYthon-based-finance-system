from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.transaction import Category, Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionListResponse, TransactionOut, TransactionUpdate


def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_transactions(
    db: Session,
    user_id: Optional[int] = None,
    type_filter: Optional[TransactionType] = None,
    category_filter: Optional[Category] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> TransactionListResponse:
    query = db.query(Transaction)

    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    if category_filter:
        query = query.filter(Transaction.category == category_filter)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    if search:
        like = f"%{search.lower()}%"
        query = query.filter(
            Transaction.description.ilike(like) | Transaction.notes.ilike(like)
        )

    total = query.count()
    total_pages = max(1, -(-total // page_size))  # ceiling division
    offset = (page - 1) * page_size
    items = query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).offset(offset).limit(page_size).all()

    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[TransactionOut.model_validate(t) for t in items],
    )


def create_transaction(db: Session, payload: TransactionCreate, user_id: int) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        description=payload.description,
        notes=payload.notes,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(db: Session, transaction: Transaction, payload: TransactionUpdate) -> Transaction:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()
