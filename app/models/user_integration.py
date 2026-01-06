from datetime import datetime

from app.models.base import MongoBaseModel, PyObjectId


class UserIntegrationModel(MongoBaseModel):
    user_id: PyObjectId
    integration_id: PyObjectId
    assigned_at: datetime
