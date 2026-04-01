import calendar
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.analytics import (
    CategoryBreakdown, DashboardOverview, FinancialSummary,
    MonthlyTotals, RecentActivity,
)


def _build_summary(transactions: list[Transaction]) -> FinancialSummary:
    income_txs = [t for t in transactions if t.type == TransactionType.income]
    expense_txs = [t for t in transactions if t.type == TransactionType.expense]

    total_income = round(sum(t.amount for t in income_txs), 2)
    total_expense = round(sum(t.amount for t in expense_txs), 2)
    current_balance = round(total_income - total_expense, 2)

    # ---- Category Breakdown ------------------------------------------------
    category_map: dict[str, dict] = {}
    for t in transactions:
        cat = t.category.value
        if cat not in category_map:
            category_map[cat] = {"total": 0.0, "count": 0}
        category_map[cat]["total"] += t.amount
        category_map[cat]["count"] += 1

    grand_total = total_income + total_expense or 1
    category_breakdown = [
        CategoryBreakdown(
            category=cat,
            total=round(data["total"], 2),
            count=data["count"],
            percentage=round((data["total"] / grand_total) * 100, 2),
        )
        for cat, data in sorted(category_map.items(), key=lambda x: x[1]["total"], reverse=True)
    ]

    # ---- Monthly Totals ----------------------------------------------------
    monthly_map: dict[tuple[int, int], dict] = {}
    for t in transactions:
        key = (t.date.year, t.date.month)
        if key not in monthly_map:
            monthly_map[key] = {"income": 0.0, "expense": 0.0}
        if t.type == TransactionType.income:
            monthly_map[key]["income"] += t.amount
        else:
            monthly_map[key]["expense"] += t.amount

    monthly_totals = [
        MonthlyTotals(
            year=year,
            month=month,
            month_name=calendar.month_name[month],
            total_income=round(data["income"], 2),
            total_expense=round(data["expense"], 2),
            net=round(data["income"] - data["expense"], 2),
        )
        for (year, month), data in sorted(monthly_map.items(), reverse=True)
    ]

    # ---- Recent Activity ---------------------------------------------------
    recent = sorted(transactions, key=lambda t: (t.date, t.created_at), reverse=True)[:10]
    recent_activity = [
        RecentActivity(
            id=t.id,
            amount=t.amount,
            type=t.type.value,
            category=t.category.value,
            date=t.date.isoformat(),
            description=t.description,
        )
        for t in recent
    ]

    return FinancialSummary(
        total_income=total_income,
        total_expense=total_expense,
        current_balance=current_balance,
        total_transactions=len(transactions),
        income_count=len(income_txs),
        expense_count=len(expense_txs),
        avg_income=round(total_income / len(income_txs), 2) if income_txs else 0.0,
        avg_expense=round(total_expense / len(expense_txs), 2) if expense_txs else 0.0,
        largest_income=round(max((t.amount for t in income_txs), default=0), 2),
        largest_expense=round(max((t.amount for t in expense_txs), default=0), 2),
        category_breakdown=category_breakdown,
        monthly_totals=monthly_totals,
        recent_activity=recent_activity,
    )


def get_summary(
    db: Session,
    user_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> FinancialSummary:
    query = db.query(Transaction)
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)
    transactions = query.all()
    return _build_summary(transactions)


def get_dashboard(db: Session, user_id: Optional[int] = None) -> DashboardOverview:
    today = date.today()
    current_month_start = today.replace(day=1)

    # Last month bounds
    if today.month == 1:
        last_month_start = today.replace(year=today.year - 1, month=12, day=1)
        last_month_end = last_month_start.replace(day=31)
    else:
        last_month_start = today.replace(month=today.month - 1, day=1)
        last_day = calendar.monthrange(today.year, today.month - 1)[1]
        last_month_end = last_month_start.replace(day=last_day)

    # Full summary (all time)
    full_summary = get_summary(db, user_id=user_id)

    # This month
    this_month_txs = _get_transactions_in_range(db, user_id, current_month_start, today)
    this_month_income = round(sum(t.amount for t in this_month_txs if t.type == TransactionType.income), 2)
    this_month_expense = round(sum(t.amount for t in this_month_txs if t.type == TransactionType.expense), 2)

    # Last month
    last_month_txs = _get_transactions_in_range(db, user_id, last_month_start, last_month_end)
    last_month_income = sum(t.amount for t in last_month_txs if t.type == TransactionType.income)
    last_month_expense = sum(t.amount for t in last_month_txs if t.type == TransactionType.expense)

    income_change_pct = _pct_change(last_month_income, this_month_income)
    expense_change_pct = _pct_change(last_month_expense, this_month_expense)

    return DashboardOverview(
        summary=full_summary,
        this_month_income=this_month_income,
        this_month_expense=this_month_expense,
        this_month_balance=round(this_month_income - this_month_expense, 2),
        income_change_pct=income_change_pct,
        expense_change_pct=expense_change_pct,
    )


def _get_transactions_in_range(
    db: Session,
    user_id: Optional[int],
    date_from: date,
    date_to: date,
) -> list[Transaction]:
    query = db.query(Transaction).filter(
        Transaction.date >= date_from,
        Transaction.date <= date_to,
    )
    if user_id is not None:
        query = query.filter(Transaction.user_id == user_id)
    return query.all()


def _pct_change(old: float, new: float) -> float:
    if old == 0:
        return 100.0 if new > 0 else 0.0
    return round(((new - old) / old) * 100, 2)
