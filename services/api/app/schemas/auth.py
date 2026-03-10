"""Schemas for authentication."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.config import settings
from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None
    nip: str | None = Field(None, pattern=r"^\d{10}$")
    regon: str | None = Field(None, pattern=r"^\d{9}(\d{5})?$")


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        """Validate passwords match."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(UserBase):
    """User response schema."""

    id: str
    is_active: bool
    is_verified: bool
    role: UserRole
    created_at: datetime
    last_login_at: datetime | None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshToken(BaseModel):
    """Refresh token schema."""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset schema."""

    token: str
    new_password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    new_password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        """Validate passwords match."""
        if self.new_password != self.new_password_confirm:
            raise ValueError("Passwords do not match")
        return self
