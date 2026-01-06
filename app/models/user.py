from pydantic import EmailStr
from enum import Enum

from app.models.base import MongoBaseModel


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEAM_LEAD = "TEAM_LEAD"
    DEVELOPER = "DEVELOPER"
    QA = "QA"
    DEVOPS = "DEVOPS"


class UserModel(MongoBaseModel):
    email: EmailStr
    name: str
    role: UserRole
    password_hash: str
    is_active: bool = True

