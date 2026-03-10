"""Schemas package."""

from app.schemas.auth import (
    PasswordReset,
    PasswordResetRequest,
    RefreshToken,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.schemas.tax import (
    TaxCalculationRequest,
    TaxCalculationResponse,
    TaxReturnCreate,
    TaxReturnResponse,
)

__all__ = [
    # Auth
    "UserCreate",
    "UserResponse",
    "TokenResponse",
    "RefreshToken",
    "PasswordResetRequest",
    "PasswordReset",
    # Document
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    # Tax
    "TaxReturnCreate",
    "TaxReturnResponse",
    "TaxCalculationRequest",
    "TaxCalculationResponse",
]
