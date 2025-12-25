from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEAM_LEAD = "TEAM_LEAD"
    DEVELOPER = "DEVELOPER"
    DEVOPS = "DEVOPS"
    QA = "QA"


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    name: str
    role: UserRole
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
