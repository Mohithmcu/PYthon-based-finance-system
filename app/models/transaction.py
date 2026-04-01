import enum

from sqlalchemy import Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Category(str, enum.Enum):
    salary = "salary"
    freelance = "freelance"
    investment = "investment"
    food = "food"
    transport = "transport"
    housing = "housing"
    utilities = "utilities"
    healthcare = "healthcare"
    entertainment = "entertainment"
    education = "education"
    shopping = "shopping"
    travel = "travel"
    other = "other"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(Category), default=Category.other, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.type}', amount={self.amount}, category='{self.category}')>"
