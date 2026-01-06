from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.base import MongoBaseModel, PyObjectId


class IntegrationModel(MongoBaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    created_by: PyObjectId
    created_at: datetime
