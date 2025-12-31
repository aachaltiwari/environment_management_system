from bson import ObjectId
from app.permissions.base import is_admin


async def can_access_environment(
    db,
    user: dict,
    environment_id: str
) -> bool:
    if not user:
        return False

    if is_admin(user):
        return True

    env = await db.environments.find_one({
        "_id": ObjectId(environment_id)
    })

    if not env:
        return False

    return user["_id"] in env.get("allowed_users", [])
