from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


# --------------------------------------------------------------------------- #
#  Request Schemas                                                             #
# --------------------------------------------------------------------------- #

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    role: UserRole = UserRole.viewer

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username cannot be empty.")
        return v.strip()


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserChangePassword(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v


# --------------------------------------------------------------------------- #
#  Response Schemas                                                            #
# --------------------------------------------------------------------------- #

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserOutBrief(BaseModel):
    id: int
    username: str
    role: UserRole

    model_config = {"from_attributes": True}


# --------------------------------------------------------------------------- #
#  Auth Schemas                                                                #
# --------------------------------------------------------------------------- #

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class TokenData(BaseModel):
    username: Optional[str] = None
