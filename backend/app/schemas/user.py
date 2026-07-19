from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    display_name: Optional[str] = None

class UserCreate(UserBase):
    clerk_id: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    xp: Optional[int] = None
    level: Optional[int] = None
    rank: Optional[str] = None
    current_streak: Optional[int] = None
    max_streak: Optional[int] = None

class UserResponse(UserBase):
    id: int
    clerk_id: str
    xp: int
    level: int
    rank: str
    current_streak: int
    max_streak: int
    last_active_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# XP History Schema
class XPHistoryResponse(BaseModel):
    id: int
    user_id: int
    amount: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True
