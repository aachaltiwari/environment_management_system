from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId
from typing import Any, Dict


class EnvironmentTypeModel(MongoBaseModel):
    name: str = Field(..., min_length=2)


class EnvironmentModel(MongoBaseModel):
    integration_id: PyObjectId
    environment_type: PyObjectId

    title: str = Field(..., min_length=2)
    content: Dict[str, Any]
    note : str | None = None

    created_by: PyObjectId
    updated_by: PyObjectId

    updated_at: datetime
