from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "AdminUserOut"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = "Administrator"
    role: Optional[str] = "admin"

class AdminUserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

Token.model_rebuild()
