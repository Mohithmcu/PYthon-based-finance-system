# 💰 Finance System Backend

A Python-powered **REST API backend** for managing and analyzing personal financial records. Built with **FastAPI**, **SQLAlchemy**, and **SQLite** — designed with clean architecture, role-based access control, and production-grade developer practices.

---

## 📦 Tech Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Framework     | FastAPI                             |
| ORM           | SQLAlchemy 2.x                      |
| Database      | SQLite (swappable to PostgreSQL)    |
| Auth          | JWT (JSON Web Tokens) via `python-jose` |
| Validation    | Pydantic v2                         |
| Password Hash | Passlib + bcrypt                    |
| Server        | Uvicorn (ASGI)                      |

---

## 🗂️ Project Structure

```
finance_backend/
├── app/
│   ├── main.py             # FastAPI app entry point, router registration
│   ├── config.py           # Settings loaded from .env
│   ├── database.py         # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── user.py         # User model + UserRole enum
│   │   └── transaction.py  # Transaction model + enums
│   ├── schemas/
│   │   ├── user.py         # Pydantic schemas for users & auth
│   │   ├── transaction.py  # Pydantic schemas for transactions
│   │   └── analytics.py    # Response schemas for analytics
│   ├── routers/
│   │   ├── auth.py         # /auth — register, login, profile, password
│   │   ├── transactions.py # /transactions — CRUD + filter + paginate
│   │   ├── analytics.py    # /analytics — summary, dashboard
│   │   ├── users.py        # /users — user management (admin)
│   │   └── export.py       # /export — CSV and JSON export
│   ├── services/
│   │   ├── user.py         # User business logic
│   │   ├── transaction.py  # Transaction business logic
│   │   └── analytics.py    # Summary, dashboard, monthly calculations
│   └── core/
│       ├── security.py     # JWT creation & verification, password hashing
│       └── dependencies.py # FastAPI dependencies: auth, role checks
├── seed_data.py            # Populate DB with realistic sample data
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone & set up the environment

```bash
cd finance_backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
copy .env.example .env   # Windows
# or
cp .env.example .env     # macOS/Linux
```

Edit `.env` if needed (defaults work for development):

```
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./finance.db
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Server starts at: **http://localhost:8000**

### 5. Seed sample data (optional but recommended)

```bash
python seed_data.py
```

This creates **4 users** and **~300 transactions** spanning 6 months.

---

## 🔐 Authentication

The API uses **JWT Bearer token** authentication.

### Register

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secret123",
  "role": "viewer"
}
```

### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=secret123
```

**Response:**
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { ... }
}
```

Use the token in all subsequent requests:
```http
Authorization: Bearer <access_token>
```

### Seed Login Credentials

| Role     | Username   | Password    |
|----------|------------|-------------|
| admin    | admin      | admin123    |
| analyst  | analyst1   | analyst123  |
| viewer   | john_doe   | john1234    |
| viewer   | jane_doe   | jane1234    |

---

## 📡 API Endpoints

### 🔑 Auth — `/api/v1/auth`

| Method | Endpoint          | Description               | Auth Required |
|--------|-------------------|---------------------------|---------------|
| POST   | `/register`       | Register a new account    | No            |
| POST   | `/login`          | Login, get JWT token      | No            |
| GET    | `/me`             | Get own profile           | Yes           |
| PUT    | `/me/password`    | Change own password       | Yes           |

---

### 💳 Transactions — `/api/v1/transactions`

| Method | Endpoint          | Description                            | Role           |
|--------|-------------------|----------------------------------------|----------------|
| GET    | `/`               | List transactions (paginated, filtered)| All            |
| POST   | `/`               | Create a new transaction               | All            |
| GET    | `/{id}`           | Get a single transaction               | All*           |
| PUT    | `/{id}`           | Update a transaction                   | Owner / Admin  |
| DELETE | `/{id}`           | Delete a transaction                   | Owner / Admin  |

**Query parameters for `GET /`:**

| Param       | Type   | Description                                  |
|-------------|--------|----------------------------------------------|
| `type`      | string | `income` or `expense`                        |
| `category`  | string | e.g. `food`, `salary`, `transport`, ...      |
| `date_from` | date   | Start date (YYYY-MM-DD)                      |
| `date_to`   | date   | End date (YYYY-MM-DD)                        |
| `search`    | string | Full-text search in description/notes        |
| `user_id`   | int    | Filter by user (admin/analyst only)          |
| `page`      | int    | Page number (default: 1)                     |
| `page_size` | int    | Records per page (default: 20, max: 100)     |

---

### 📊 Analytics — `/api/v1/analytics`

| Method | Endpoint       | Description                                          | Role     |
|--------|----------------|------------------------------------------------------|----------|
| GET    | `/summary`     | Full financial summary (income, expenses, breakdown) | All*     |
| GET    | `/dashboard`   | Dashboard overview with month-over-month comparison  | All*     |

**Summary includes:**
- Total income / expenses / balance
- Average income & expense per transaction
- Largest single income & expense
- Category-wise breakdown with percentages
- Month-by-month totals (income, expense, net)
- 10 most recent transactions

**Dashboard includes:**
- Everything from summary
- This month's income/expense vs last month (% change)

---

### 👥 Users — `/api/v1/users`

| Method | Endpoint     | Description                  | Role          |
|--------|--------------|------------------------------|---------------|
| GET    | `/`          | List all users (paginated)   | Admin only    |
| GET    | `/{id}`      | Get user by ID               | Owner / Admin |
| PUT    | `/{id}`      | Update user profile/role     | Owner / Admin |
| DELETE | `/{id}`      | Delete a user                | Admin only    |

---

### 📤 Export — `/api/v1/export`

| Method | Endpoint  | Description                      | Role  |
|--------|-----------|----------------------------------|-------|
| GET    | `/csv`    | Download transactions as CSV     | All   |
| GET    | `/json`   | Download transactions as JSON    | All   |

Supports the same filters as the transactions list endpoint.

---

## 👮 Role-Based Access Control

| Permission                  | Viewer | Analyst | Admin |
|-----------------------------|--------|---------|-------|
| View own transactions       | ✅     | ✅      | ✅    |
| View all users' transactions| ❌     | ✅      | ✅    |
| View own analytics          | ✅     | ✅      | ✅    |
| View all users' analytics   | ❌     | ✅      | ✅    |
| Create transactions         | ✅     | ✅      | ✅    |
| Update own transactions     | ✅     | ✅      | ✅    |
| Delete own transactions     | ✅     | ✅      | ✅    |
| Update/delete any record    | ❌     | ❌      | ✅    |
| Manage users                | ❌     | ❌      | ✅    |
| Assign roles                | ❌     | ❌      | ✅    |

---

## 🗃️ Data Models

### User

| Field           | Type    | Description                    |
|-----------------|---------|--------------------------------|
| id              | int     | Primary key                    |
| username        | string  | Unique username                |
| email           | string  | Unique email address           |
| full_name       | string  | Optional display name          |
| hashed_password | string  | Bcrypt hashed                  |
| role            | enum    | `viewer`, `analyst`, `admin`   |
| is_active       | bool    | Account status                 |
| created_at      | datetime| Auto-set on creation           |

### Transaction

| Field       | Type    | Description                                        |
|-------------|---------|----------------------------------------------------|
| id          | int     | Primary key                                        |
| user_id     | int     | FK → users.id                                      |
| amount      | float   | Positive decimal value                             |
| type        | enum    | `income` or `expense`                              |
| category    | enum    | salary, food, housing, transport, etc.             |
| date        | date    | Transaction date                                   |
| description | string  | Short description                                  |
| notes       | string  | Optional longer notes                              |
| created_at  | datetime| Auto-set on creation                               |

### Available Categories

`salary` · `freelance` · `investment` · `food` · `transport` · `housing` · `utilities` · `healthcare` · `entertainment` · `education` · `shopping` · `travel` · `other`

---

## 🧪 Testing with Swagger UI

Navigate to **[http://localhost:8000/docs](http://localhost:8000/docs)** for the interactive Swagger UI.

Steps:
1. Use `POST /api/v1/auth/login` to get a JWT token
2. Click **"Authorize"** (top right) and paste: `Bearer <your_token>`
3. All endpoints are now authenticated — try them out!

Alternative docs: **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

---

## 🔄 Switching to PostgreSQL

In `.env`, change:
```
DATABASE_URL=postgresql://user:password@localhost:5432/finance_db
```

Remove the `connect_args` in `database.py` (SQLite-specific) and install:
```bash
pip install psycopg2-binary
```

---

## 📝 Assumptions Made

1. **Single database (SQLite)** — chosen for zero-config setup; easily swappable.
2. **Soft role model** — roles are stored per-user and enforced at the API layer.
3. **Viewers cannot see other users' data** — enforced in both services and routers.
4. **Transaction ownership** — transactions belong to the user who created them.
5. **All amounts are positive** — type (`income`/`expense`) determines the direction.
6. **No email verification** — out of scope for a backend assessment.

---

## 📋 Summary of Features

- ✅ JWT authentication (register, login, token refresh-like with re-login)
- ✅ Role-based access control (viewer / analyst / admin)
- ✅ Full CRUD for financial transactions
- ✅ Advanced filtering: by type, category, date range, and text search
- ✅ Pagination on all list endpoints
- ✅ Financial analytics: summary, balance, category breakdown, monthly totals
- ✅ Dashboard with month-over-month comparison
- ✅ CSV and JSON export with filters applied
- ✅ Clean layered architecture (models → services → routers)
- ✅ Comprehensive input validation with meaningful error responses
- ✅ Auto-generated interactive API docs (Swagger + ReDoc)
- ✅ Seed script for realistic sample data
