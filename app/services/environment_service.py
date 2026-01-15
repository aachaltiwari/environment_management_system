from datetime import datetime
from pymongo.errors import DuplicateKeyError
from app.graphql.errors import UserInputError
from app.utils.objectid import parse_object_id

##### list_environments service function #####
async def list_environments(db, integration_id):
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

    return result



##### get environment by id service function #####
async def get_environment(db, environment_id):
    env_oid = parse_object_id(environment_id, "environmentId")

    env = await db.environments.find_one({"_id": env_oid})
    return env


##### create environment service function #####
async def create_environment(db, user, integration_id, data):
    integration_oid = parse_object_id(integration_id, "integrationId")

    env = {
        "integration_id": integration_oid,
        "environment_type": data["environmentType"],
        "title": data["title"],
        "content": data["content"],
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
    return env



##### update environment service function #####
async def update_environment(db, user, integration_id, environment_id, data
):
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

    return env


##### delete environment service function #####
async def delete_environment(db, environment_id, integration_id):
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



