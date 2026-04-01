"""
Seed script — populates the database with realistic sample data.
Run once after starting the app for the first time:
    python seed_data.py
"""
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, ".")  # ensure app is importable

from app.database import Base, SessionLocal, engine
from app.models import User, Transaction, UserRole, TransactionType, Category
from app.core.security import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Clear existing data ──────────────────────────────────────────────────────
print("Clearing existing data...")
db.query(Transaction).delete()
db.query(User).delete()
db.commit()

# ── Create seed users ────────────────────────────────────────────────────────
print("Creating users...")

users_data = [
    dict(username="admin",    email="admin@finance.local",   full_name="Admin User",    password="admin123",   role=UserRole.admin),
    dict(username="analyst1", email="analyst@finance.local", full_name="Sarah Analyst", password="analyst123", role=UserRole.analyst),
    dict(username="john_doe", email="john@example.com",      full_name="John Doe",      password="john1234",   role=UserRole.viewer),
    dict(username="jane_doe", email="jane@example.com",      full_name="Jane Doe",      password="jane1234",   role=UserRole.viewer),
]

created_users = []
for u in users_data:
    user = User(
        username=u["username"],
        email=u["email"],
        full_name=u["full_name"],
        hashed_password=get_password_hash(u["password"]),
        role=u["role"],
        is_active=True,
    )
    db.add(user)
    created_users.append(user)

db.commit()
for u in created_users:
    db.refresh(u)

print(f"  ✓ {len(created_users)} users created")

# ── Seed transactions ────────────────────────────────────────────────────────
print("Creating transactions...")

income_templates = [
    (TransactionType.income, Category.salary,     "Monthly salary payment",  3000, 8000),
    (TransactionType.income, Category.freelance,  "Freelance project payment", 500, 3000),
    (TransactionType.income, Category.investment, "Dividend payout",           100, 2000),
]

expense_templates = [
    (TransactionType.expense, Category.food,          "Groceries & dining",      50,  400),
    (TransactionType.expense, Category.transport,     "Fuel / Uber rides",       20,  200),
    (TransactionType.expense, Category.housing,       "Rent payment",           800, 1800),
    (TransactionType.expense, Category.utilities,     "Electricity & internet",  50,  200),
    (TransactionType.expense, Category.healthcare,    "Doctor / pharmacy",       30,  300),
    (TransactionType.expense, Category.entertainment, "Movies / streaming",      10,  150),
    (TransactionType.expense, Category.education,     "Online course / books",   20,  500),
    (TransactionType.expense, Category.shopping,      "Clothing / electronics",  50,  600),
    (TransactionType.expense, Category.travel,        "Weekend trip",           100, 1000),
]

all_templates = income_templates + expense_templates

today = date.today()
total_transactions = 0

for user in created_users:
    # create 6 months of transactions
    for month_offset in range(6):
        tx_date_start = today.replace(day=1) - timedelta(days=month_offset * 30)

        num_transactions = random.randint(10, 18)
        for _ in range(num_transactions):
            template = random.choice(all_templates)
            tx_type, cat, desc, lo, hi = template

            amount = round(random.uniform(lo, hi), 2)

            day_offset = random.randint(0, 27)
            tx_date = tx_date_start + timedelta(days=day_offset)
            if tx_date > today:
                tx_date = today

            tx = Transaction(
                user_id=user.id,
                amount=amount,
                type=tx_type,
                category=cat,
                date=tx_date,
                description=desc,
                notes=random.choice([None, "Auto-generated seed record", "Reviewed"]),
            )
            db.add(tx)
            total_transactions += 1

db.commit()
print(f"  ✓ {total_transactions} transactions created across {len(created_users)} users")

db.close()

print("\n✅ Seed complete! Login credentials:")
print("  Role     | Username   | Password")
print("  ---------|------------|----------")
for u in users_data:
    print(f"  {u['role'].value:<8} | {u['username']:<10} | {u['password']}")

print("\n  API docs: http://localhost:8000/docs")
