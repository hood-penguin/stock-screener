"""Pydantic schemas for user-related API requests/responses."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255, description="Password (min 8 chars)")
    display_name: str | None = Field(None, max_length=100)


class UserLoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Expiration time in seconds")


class UserResponse(BaseModel):
    """User profile response."""

    id: int
    email: str
    display_name: str | None
    tier: str = Field("free", description="Subscription tier (free, premium)")
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WatchlistItemResponse(BaseModel):
    """Watchlist item."""

    id: int
    stock_id: int
    stock_ticker: str | None = None
    alert_threshold: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class WatchlistResponse(BaseModel):
    """User's watchlist."""

    items: list[WatchlistItemResponse]
    total: int


class ScreeningPresetRequest(BaseModel):
    """Request to create or update screening preset."""

    preset_name: str = Field(..., min_length=1, max_length=100)
    is_default: bool = False
    enabled_criteria: dict[str, bool] = Field(
        default_factory=dict,
        description="Which criteria are enabled"
    )
    weight_overrides: dict[str, float] = Field(
        default_factory=dict,
        description="Custom weights for criteria"
    )
    min_score: float | None = Field(None, ge=0, le=1)


class ScreeningPresetResponse(ScreeningPresetRequest):
    """Screening preset response."""

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
