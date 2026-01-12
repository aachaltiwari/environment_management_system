from bson import ObjectId
from app.permissions.base import is_admin, is_team_lead


async def can_manupulate_integration(user: dict) -> bool:
    if not user:
        return False
    return is_admin(user) or is_team_lead(user)
