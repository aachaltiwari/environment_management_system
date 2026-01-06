from bson import ObjectId
from app.permissions.base import is_admin, is_team_lead


async def can_create_integration(user: dict) -> bool:
    if not user:
        return False
    return is_admin(user) or is_team_lead(user)


async def can_manage_integration(db, user: dict, integration_id: str) -> bool:
    if not user:
        return False

    if is_admin(user):
        return True

    if not is_team_lead(user):
        return False

    mapping = await db.user_integrations.find_one({
        "user_id": user["_id"],
        "integration_id": ObjectId(integration_id),
    })

    return mapping is not None
