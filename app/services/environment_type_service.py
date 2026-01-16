from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.graphql.errors import UserInputError
from app.utils.objectid import parse_object_id


async def create_environment_type(db, user, name: str| None):
    if not name or not name.strip():
        raise UserInputError("Environment type name is required")

    env_type = {
        "name": name.strip(),
        "created_by": user["_id"],
        "created_at": datetime.utcnow(),
    }

    try:
        result = await db.environment_types.insert_one(env_type)
    except DuplicateKeyError:
        raise UserInputError("Environment type already exists")

    return {
        "id": str(result.inserted_id),
        "name": env_type["name"],
        "createdAt": env_type["created_at"].isoformat(),
    }


##### list environment types service function #####
async def list_environment_types(db):
    types = []

    cursor = db.environment_types.find({})
    async for t in cursor:
        types.append({
            "id": str(t["_id"]),
            "name": t["name"],
            "createdAt": t["created_at"].isoformat(),   
            "createdBy": str(t["created_by"]),
        })

    return types
