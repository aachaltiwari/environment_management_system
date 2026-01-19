from datetime import datetime
from pymongo.errors import DuplicateKeyError
from app.graphql.errors import UserInputError
from app.utils.objectid import parse_object_id

##### list_environments service function #####
async def list_environments(db, integration_id: str)-> list[dict] :
    integration_oid = parse_object_id(integration_id, "integrationId")

    integrations = await db.integrations.find_one({
        "_id": integration_oid,
        "is_deleted": False,
    })

    if not integrations:
        raise UserInputError("Integration does not exist or is deleted")

    cursor = db.environments.find({"integration_id": integration_oid})

    result = []
    async for env in cursor:
        result.append(env)

    return [serialize_environment(env) for env in result]



##### get environment by id service function #####
async def get_environment(db, environment_id: str) -> dict | None:
    env_oid = parse_object_id(environment_id, "environmentId")

    env = await db.environments.find_one({"_id": env_oid})
    return serialize_environment(env) if env else None


##### create environment service function #####
async def create_environment(db, user, integration_id, data):
    integration_oid = parse_object_id(integration_id, "integrationId")

     # Validate environment type exists
    env_type = await db.environment_types.find_one({
        "name": data["environmentType"]
    })

    if not env_type:
        raise UserInputError(
            f"Environment type '{data['environmentType']}' does not exist"
        )

    env = {
        "integration_id": integration_oid,
        "environment_type": data["environmentType"],
        "title": data["title"],
        "content": data["content"],
        "note": data.get("note"),
        "created_by": user["_id"],
        "updated_by": user["_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        result = await db.environments.insert_one(env)
    except DuplicateKeyError:
        raise UserInputError(
            "Environment already exists for this integration and type"
        )

    env["_id"] = result.inserted_id
    return serialize_environment(env)



##### update environment service function #####
async def update_environment(db, user, integration_id: str, environment_id: str, data)-> dict:
    env_oid = parse_object_id(environment_id, "environmentId")
    integration_oid = parse_object_id(integration_id, "integrationId")

    update = {
        "updated_by": user["_id"],
        "updated_at": datetime.utcnow(),
    }

    if data.get("title") is not None:
        update["title"] = data["title"]

    if data.get("content") is not None:
        update["content"] = data["content"]

    if len(update) == 2:
        raise UserInputError("Nothing to update")

   
    env = await db.environments.find_one_and_update(
        {
            "_id": env_oid,
            "integration_id": integration_oid,
        },
        {"$set": update},
        return_document=True,
    )

    if not env:
        raise UserInputError(
            "Environment not found for this integration"
        )

    return serialize_environment(env)


##### delete environment service function #####
async def delete_environment(db, environment_id: str, integration_id: str) -> bool:
    env_oid = parse_object_id(environment_id, "environmentId")
    integration_oid = parse_object_id(integration_id, "integrationId")

    if not await db.environments.find_one({
        "_id": env_oid,
        "integration_id": integration_oid,
    }):
        raise UserInputError("Environment not found for this integration")

    result = await db.environments.delete_one({"_id": env_oid})

    if result.deleted_count == 0:
        raise UserInputError("Environment not found")

    return True


##### environment serialize function #####
def serialize_environment(env: dict) -> dict:
    return {
        "id": str(env["_id"]),
        "integrationId": str(env["integration_id"]),
        "environmentType": str(env["environment_type"]),
        "title": env["title"],
        "content": env["content"],
        "note": env.get("note"),
        "createdBy": str(env["created_by"]),
        "updatedBy": str(env["updated_by"]),
        "createdAt": env["created_at"],
        "updatedAt": env["updated_at"],
    }