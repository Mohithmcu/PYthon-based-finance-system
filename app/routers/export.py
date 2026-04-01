import csv
import io
import json
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, require_analyst
from app.database import get_db
from app.models.transaction import Category, Transaction, TransactionType
from app.models.user import User, UserRole

router = APIRouter(prefix="/export", tags=["Export"])


def _fetch(
    db: Session,
    user_id: Optional[int],
    type_filter: Optional[TransactionType],
    category_filter: Optional[Category],
    date_from: Optional[date],
    date_to: Optional[date],
) -> list[Transaction]:
    q = db.query(Transaction)
    if user_id is not None:
        q = q.filter(Transaction.user_id == user_id)
    if type_filter:
        q = q.filter(Transaction.type == type_filter)
    if category_filter:
        q = q.filter(Transaction.category == category_filter)
    if date_from:
        q = q.filter(Transaction.date >= date_from)
    if date_to:
        q = q.filter(Transaction.date <= date_to)
    return q.order_by(Transaction.date.desc()).all()


def _rows(transactions: list[Transaction]) -> list[dict]:
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "amount": t.amount,
            "type": t.type.value,
            "category": t.category.value,
            "date": t.date.isoformat(),
            "description": t.description or "",
            "notes": t.notes or "",
            "created_at": t.created_at.isoformat() if t.created_at else "",
        }
        for t in transactions
    ]


@router.get("/csv")
def export_csv(
    type: Optional[TransactionType] = Query(None),
    category: Optional[Category] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Export transactions as a CSV file."""
    uid = current_user.id if current_user.role == UserRole.viewer else user_id
    transactions = _fetch(db, uid, type, category, date_from, date_to)
    rows = _rows(transactions)

    buffer = io.StringIO()
    if rows:
        writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("/json")
def export_json(
    type: Optional[TransactionType] = Query(None),
    category: Optional[Category] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Export transactions as a JSON file."""
    uid = current_user.id if current_user.role == UserRole.viewer else user_id
    transactions = _fetch(db, uid, type, category, date_from, date_to)
    rows = _rows(transactions)

    content = json.dumps({"count": len(rows), "transactions": rows}, indent=2)
    return StreamingResponse(
        io.StringIO(content),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=transactions.json"},
    )
