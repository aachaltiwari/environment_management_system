from bson import ObjectId
from app.graphql.errors import UserInputError
from datetime import datetime
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.utils.objectid import parse_object_id
from app.graphql.errors import UserInputError


# -------------------------
# LIST ALL INTEGRATIONS
# -------------------------

async def get_integrations(db)-> list[dict]:
    integrations = []

    cursor = db.integrations.find({"is_deleted": False})

    async for integ in cursor:
        integrations.append(_serialize_integration(integ))

    return integrations


# -------------------------
# GET SINGLE INTEGRATION
# -------------------------

async def get_integration_by_id(db, integration_oid: ObjectId):
    integ = await db.integrations.find_one({
        "_id": integration_oid,
        "is_deleted": False,
    })

    if not integ:
        return None

    return _serialize_integration(integ)


# -------------------------
# USER → INTEGRATIONS
# -------------------------

async def get_user_integrations(db, user_oid: ObjectId):
    # Validate user
    user = await db.users.find_one({
        "_id": user_oid,
        "is_active": True,
    })

    if not user:
        raise UserInputError("User is either non-existent or inactive")

    integrations = []

    cursor = db.user_integrations.find({"user_id": user_oid})

    async for mapping in cursor:
        integ = await db.integrations.find_one({
            "_id": mapping["integration_id"],
            "is_deleted": False,
        })

        if integ:
            integrations.append(_serialize_integration(integ))

    return integrations




##### createIntegration mutation #####
# -------------------------
# CREATE INTEGRATION
# -------------------------
async def create_integration(db, user: dict, input: dict):
    integration = {
        "name": input["name"].strip(),
        "description": input.get("description"),
        "created_by": user["_id"],
        "created_at": datetime.utcnow(),
        "is_deleted": False,
    }

    try:
        result = await db.integrations.insert_one(integration)
    except DuplicateKeyError:
        raise UserInputError("Integration with this name already exists")

    # Optionally assign a user
    assigned_user_id = input.get("assignedUserId")
    if assigned_user_id:
        user_oid = parse_object_id(assigned_user_id, "assignedUserId")
        assigned_user = await db.users.find_one({
            "_id": user_oid,
            "is_active": True
        })
        if not assigned_user:
            raise UserInputError("Assigned user does not exist or inactive. Integration created.")

        try:
            await db.user_integrations.insert_one({
                "user_id": user_oid,
                "integration_id": result.inserted_id,
                "assigned_at": datetime.utcnow(),
            })
        except DuplicateKeyError:
            # already assigned, ignore
            pass

    integration["_id"] = result.inserted_id
    return _serialize_integration(integration)


# -------------------------
# ASSIGN USER TO INTEGRATION
# -------------------------
async def assign_user_to_integration(db, integrationId, userId):
    integration_oid = parse_object_id(integrationId, "integrationId")
    user_oid = parse_object_id(userId, "userId")

    # Validate integration
    integration = await db.integrations.find_one({
        "_id": integration_oid,
        "is_deleted": False
    })
    if not integration:
        raise UserInputError("Integration is either non-existent or deleted")

    # Validate user
    user = await db.users.find_one({
        "_id": user_oid,
        "is_active": True
    })
    if not user:
        raise UserInputError("User is either non-existent or inactive")

    try:
        await db.user_integrations.insert_one({
            "user_id": user_oid,
            "integration_id": integration_oid,
            "assigned_at": datetime.utcnow(),
        })
    except DuplicateKeyError:
        raise UserInputError("User already assigned to this integration")

    return True


# -------------------------
# UPDATE INTEGRATION
# -------------------------
async def update_integration(db, integrationId, input: dict):
    integration_oid = parse_object_id(integrationId, "integrationId")

    # Check integration exists
    integration = await db.integrations.find_one({
        "_id": integration_oid,
        "is_deleted": False
    })
    if not integration:
        raise UserInputError("Integration is either non-existent or deleted")

    update = {}
    if input.get("name"):
        update["name"] = input["name"].strip()
    if input.get("description"):
        update["description"] = input["description"]

    if not update:
        raise UserInputError("Nothing to update")

    try:
        await db.integrations.update_one(
            {"_id": integration_oid},
            {"$set": update},
        )
    except DuplicateKeyError:
        raise UserInputError("Integration with this name already exists")

    updated_integration = await db.integrations.find_one({"_id": integration_oid})
    return _serialize_integration(updated_integration)


# -------------------------
# DELETE (SOFT DELETE) INTEGRATION
# -------------------------
async def soft_delete_integration(db, integrationId):
    integration_oid = parse_object_id(integrationId, "integrationId")

    integration = await db.integrations.find_one({
        "_id": integration_oid,
        "is_deleted": False
    })
    if not integration:
        raise UserInputError("Integration is either non-existent or deleted")

    await db.integrations.update_one(
        {"_id": integration_oid},
        {"$set": {"is_deleted": True, "deleted_at": datetime.utcnow()}}
    )

    return True


# -------------------------
# REMOVE USER FROM INTEGRATION
# -------------------------
async def remove_user_from_integration(db, integrationId, userId):
    integration_oid = parse_object_id(integrationId, "integrationId")
    user_oid = parse_object_id(userId, "userId")

    mapping = await db.user_integrations.find_one({
        "user_id": user_oid,
        "integration_id": integration_oid,
    })

    if not mapping:
        raise UserInputError("User is not assigned to this integration")

    await db.user_integrations.delete_one({"_id": mapping["_id"]})
    return True


#-------------------------
# SERIALIZER
# -------------------------
def _serialize_integration(integ: dict) -> dict:
    return {
        "id": str(integ["_id"]),
        "name": integ["name"],
        "description": integ.get("description"),
        "createdBy": str(integ["created_by"]),
        "createdAt": integ["created_at"].isoformat(),
        "isDeleted": integ.get("is_deleted", False),
    }
