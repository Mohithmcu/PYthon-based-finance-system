from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import verify_password, get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
) -> tuple[list[User], int]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, payload: UserCreate) -> User:
    hashed_pwd = get_password_hash(payload.password)
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hashed_pwd,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, payload: UserUpdate) -> User:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, new_password: str) -> User:
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
