from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import (
    auth_router, transactions_router, analytics_router,
    users_router, export_router,
)

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance System API",
    description=(
        "A Python-based Finance Tracking System Backend. "
        "Supports financial records management, analytics, role-based access control, "
        "JWT authentication, and CSV/JSON export."
    ),
    version="1.0.0",
    contact={"name": "Finance System"},
    license_info={"name": "MIT"},
)

# CORS — open for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(transactions_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
app.include_router(users_router, prefix=API_PREFIX)
app.include_router(export_router, prefix=API_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Finance System API is running.",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
