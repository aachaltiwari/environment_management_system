from bson import ObjectId
from app.permissions.base import is_admin, is_team_lead


async def can_manage_integration(db, user: dict, integration_id: str) -> bool:
    if not user:
        return False

    if is_admin(user):
        return True

    if not is_team_lead(user):
        return False

    integration = await db.integrations.find_one({
        "_id": ObjectId(integration_id)
    })

    if not integration:
        return False

    return integration["owner_id"] == user["_id"]
