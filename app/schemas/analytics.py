from typing import Optional

from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    percentage: float


class MonthlyTotals(BaseModel):
    year: int
    month: int
    month_name: str
    total_income: float
    total_expense: float
    net: float


class RecentActivity(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: str
    description: Optional[str]


class FinancialSummary(BaseModel):
    total_income: float
    total_expense: float
    current_balance: float
    total_transactions: int
    income_count: int
    expense_count: int
    avg_income: float
    avg_expense: float
    largest_income: float
    largest_expense: float
    category_breakdown: list[CategoryBreakdown]
    monthly_totals: list[MonthlyTotals]
    recent_activity: list[RecentActivity]


class DashboardOverview(BaseModel):
    summary: FinancialSummary
    this_month_income: float
    this_month_expense: float
    this_month_balance: float
    income_change_pct: float   # compared to last month
    expense_change_pct: float  # compared to last month
