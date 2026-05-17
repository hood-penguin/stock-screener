from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    """사용자 정보 응답"""
    id: int
    email: str
    name: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
