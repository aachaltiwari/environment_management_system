from bdb import Breakpoint
from ariadne import MutationType
from bson import ObjectId
from bson.errors import InvalidId
from jose import JWTError
from datetime import datetime

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.graphql.decorators import requires_admin, requires_integration_manupulation
from app.models.user import UserRole
from app.graphql.errors import UserInputError, AuthenticationError

from pymongo.errors import DuplicateKeyError

from app.utils.objectid import parse_object_id


mutation = MutationType()

##### login mutation #####

@mutation.field("login")
async def resolve_login(_, info, email, password):
    db = info.context["db"]

    user = await db.users.find_one({"email": email})

    if not user or not verify_password(password, user["password_hash"]):
        raise AuthenticationError("Invalid email or password")

    if not user.get("is_active", False):
        raise AuthenticationError("User account is inactive")

    return {
        "accessToken": create_access_token(
            str(user["_id"]), user["role"]
        ),
        "refreshToken": create_refresh_token(
            str(user["_id"])
        ),
    }

##### refreshToken mutation #####

@mutation.field("refreshToken")
async def resolve_refresh(_, info, refreshToken):
    try:
        payload = decode_token(refreshToken)
    except JWTError:
        raise AuthenticationError("Invalid refresh token")

    if payload.get("token_type") != "refresh":
        raise AuthenticationError("Invalid token type")

    user_id = payload.get("sub")
    db = info.context["db"]

    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user or not user.get("is_active", False):
        raise AuthenticationError("User not found or inactive")

    return {
        "accessToken": create_access_token(
            str(user["_id"]), user["role"]
        )
    }


##### createUser mutation #####

@mutation.field("createUser")
@requires_admin
async def resolve_create_user(_, info, input):
    db = info.context["db"]

    email = input["email"].lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise UserInputError("User with this email already exists")

    if input["role"] not in UserRole.__members__:
        raise UserInputError("Invalid role")

    user = {
        "email": email,
        "name": input["name"],
        "role": input["role"],
        "password_hash": hash_password(input["password"]),
        "is_active": True,
    }

    result = await db.users.insert_one(user)

    return {
        "id": str(result.inserted_id),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "isActive": user["is_active"],
    }


##### setUserActive mutation #####

@mutation.field("updateUser")
@requires_admin
async def resolve_update_user(_, info, userId, input):
    db = info.context["db"]

    user_oid = parse_object_id(userId, "userId")

    update_data = {}

    # Allowed fields only
    if input.get("name") is not None:
        update_data["name"] = input["name"].strip()

    if input.get("role") is not None:
        if input["role"] not in UserRole.__members__:
            raise UserInputError("Invalid role")
        update_data["role"] = input["role"]

    if input.get("isActive") is not None:
        update_data["is_active"] = input["isActive"]
        
    if not update_data:
        raise UserInputError("No valid fields provided for update")

    result = await db.users.find_one_and_update(
        {"_id": ObjectId(user_oid)},
        {"$set": update_data},
        return_document=True,
    )

    if not result:
        raise UserInputError("User not found")

    return {
        "id": str(result["_id"]),
        "email": result["email"],
        "name": result["name"],
        "role": result["role"],
        "isActive": result["is_active"],
    }

##### create integration mutation #####

@mutation.field("createIntegration")
@requires_integration_manupulation
async def resolve_create_integration(_, info, input):
    db = info.context["db"]

    integration = {
        "name": input["name"].strip(),
        "description": input.get("description"),
        "created_by": info.context["user"]["_id"],
        "created_at": datetime.utcnow(),
        "is_deleted": False,
    }

    try:
        result = await db.integrations.insert_one(integration)
    except DuplicateKeyError:
        raise UserInputError(
            "Integration with this name already exists"
        )
    
    if input.get("assignedUserId"):
        user_oid = parse_object_id(input["assignedUserId"], "assignedUserId")
        user = await db.users.find_one({
            "_id": user_oid(input["assignedUserId"]),
            "is_active": True
        })

        if not user:
            raise UserInputError(
                "Assigned user does not exist. Integration is created"
            )

        if not user.get("is_active", False):
            raise UserInputError(
                "Assigned user is inactive. Integration is created"
            )

        try:
            await db.user_integrations.insert_one({
                "user_id": user["_id"],
                "integration_id": result.inserted_id,
                "assigned_at": datetime.utcnow(),
            })
        except DuplicateKeyError:
            pass

    return {
        "id": str(result.inserted_id),
        "name": integration["name"],
        "description": integration["description"],
        "createdBy": str(integration["created_by"]),
        "createdAt": integration["created_at"].isoformat(),
        "isDeleted": integration["is_deleted"],
    }


##### assignUserToIntegration mutation #####
@mutation.field("assignUserToIntegration")
@requires_integration_manupulation
async def resolve_assign_user(_, info, integrationId, userId):
    db = info.context["db"]

    # Validate integration exists
    integration_oid = parse_object_id(integrationId, "integrationId")

    integration = await db.integrations.find_one({
        "_id": integration_oid, "is_deleted": False
    })
    if not integration:
        raise UserInputError("Integration is either non-existent or deleted")

    # Validate user exists
    user_oid = parse_object_id(userId, "userId")
    user = await db.users.find_one({
        "_id": user_oid, "is_active": True
    })
    if not user:
        raise UserInputError("User is either non-existent or inactive")

    # Assign user (DB enforces uniqueness)
    try:
        await db.user_integrations.insert_one({
            "user_id": user_oid,
            "integration_id": integration_oid,
            "assigned_at": datetime.utcnow(),
        })
    except DuplicateKeyError:
        raise UserInputError("User already assigned to this integration")

    return True


##### updateIntegration mutation #####
@mutation.field("updateIntegration")
@requires_integration_manupulation
async def resolve_update_integration(_, info, integrationId, input):
    db = info.context["db"]

    #Check integration exists
    integration_oid = parse_object_id(integrationId, "integrationId")   
    integration = await db.integrations.find_one({
        "_id": integration_oid , "is_deleted": False
    })
    if not integration:
        raise UserInputError("Integration is either non-existent or deleted")

    update = {}

    if input.get("name"):
        update["name"] = input["name"]
    
    if input.get("description"):
        update["description"] = input["description"]

    if not update:
        raise UserInputError("Nothing to update")

    try:
        await db.integrations.update_one(
            {"_id": ObjectId(integrationId)},
            {"$set": update},
        )
    except DuplicateKeyError:
        raise UserInputError(
            "Integration with this name already exists"
        )

    integ = await db.integrations.find_one({
        "_id": integration_oid
    })

    return {
        "id": str(integ["_id"]),
        "name": integ["name"],
        "description": integ.get("description"),
        "createdBy": str(integ["created_by"]),
        "createdAt": integ["created_at"].isoformat(),
    }



##### deleteIntegration mutation #####
@mutation.field("deleteIntegration")
@requires_integration_manupulation
async def resolve_delete_integration(_, info, integrationId):
    db = info.context["db"]

    #Check integration exists
    integration_oid = parse_object_id(integrationId, "integrationId")
    integration = await db.integrations.find_one({
        "_id": integration_oid, "is_deleted": False
    })
    if not integration:
        raise UserInputError("Integration is either non-existent or deleted")


    await db.integrations.update_one({
        "_id": integration_oid},
        {"$set": {
            "is_deleted": True,
            "deleted_at": datetime.utcnow()
        }
    })

    
    return True



#### remove user from integration mutation #####
@mutation.field("removeUserFromIntegration")
@requires_integration_manupulation
async def resolve_remove_user(_, info, integrationId, userId):
    db = info.context["db"]

    integration_oid = parse_object_id(integrationId, "integrationId")
    user_oid = parse_object_id(userId, "userId")

    mapping = await db.user_integrations.find_one({
        "user_id": user_oid,
        "integration_id": integration_oid,
    })

    if not mapping:
        raise UserInputError(
            "User is not assigned to this integration"
        )

    await db.user_integrations.delete_one({
        "_id": mapping["_id"]
    })

    return True

