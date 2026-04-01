from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.transaction import Category, TransactionType


# --------------------------------------------------------------------------- #
#  Request Schemas                                                             #
# --------------------------------------------------------------------------- #

class TransactionCreate(BaseModel):
    amount: float
    type: TransactionType
    category: Category = Category.other
    date: date
    description: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be a positive number.")
        return round(v, 2)


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[Category] = None
    date: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be a positive number.")
        return round(v, 2) if v else v


# --------------------------------------------------------------------------- #
#  Response Schemas                                                            #
# --------------------------------------------------------------------------- #

class TransactionOut(BaseModel):
    id: int
    user_id: int
    amount: float
    type: TransactionType
    category: Category
    date: date
    description: Optional[str]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[TransactionOut]
