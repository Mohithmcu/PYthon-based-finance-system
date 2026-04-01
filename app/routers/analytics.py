from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, require_analyst
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import DashboardOverview, FinancialSummary
from app.services.analytics import get_dashboard, get_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _scope_user_id(current_user: User, requested_uid: Optional[int]) -> Optional[int]:
    if current_user.role == UserRole.viewer:
        return current_user.id               # viewers only see their own
    return requested_uid                     # analysts/admins can pass a user_id or None for all


@router.get("/summary", response_model=FinancialSummary)
def financial_summary(
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
    user_id: Optional[int] = Query(None, description="Target user (admin/analyst only)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return a full financial summary including income, expenses, balance,
    category breakdown, monthly totals, and recent activity.

    - **Viewers** see only their own summary.
    - **Analysts/Admins** may query any user or all users.
    """
    uid = _scope_user_id(current_user, user_id)
    return get_summary(db, user_id=uid, date_from=date_from, date_to=date_to)


@router.get("/dashboard", response_model=DashboardOverview)
def dashboard(
    user_id: Optional[int] = Query(None, description="Target user (admin/analyst only)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Return a dashboard overview including this-month stats vs last-month percentage change.
    """
    uid = _scope_user_id(current_user, user_id)
    return get_dashboard(db, user_id=uid)
