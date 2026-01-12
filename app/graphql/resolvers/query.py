from ariadne import QueryType
from bson import ObjectId
from app.graphql.decorators import requires_admin, requires_auth
from app.utils.objectid import parse_object_id

query = QueryType()


@query.field("me")
@requires_auth
async def resolve_me(_, info):
    user = info.context["user"]
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }


@query.field("users")
# @requires_admin
async def resolve_users(_, info):
    db = info.context["db"]

    users = await db.users.find({"is_active": True}).to_list(length=None)

    return [
        {
            "id": str(u["_id"]),
            "email": u["email"],
            "name": u["name"],
            "role": u["role"],
            "isActive": u["is_active"],
        }
        for u in users
    ]


@query.field("integrations")
@requires_auth
async def resolve_integrations(_, info):
    db = info.context["db"]

    integrations = []

    cursor = db.integrations.find({"is_deleted": False})
    async for integ in cursor:
        integrations.append({
            "id": str(integ["_id"]),
            "name": integ["name"],
            "description": integ.get("description"),
            "createdBy": str(integ["created_by"]),
            "createdAt": integ["created_at"].isoformat(),
        })

    return integrations


@query.field("integration")
@requires_auth
async def resolve_integration(_, info, integrationId):
    db = info.context["db"]
    # breakpoint()

    integ = await db.integrations.find_one({
        "_id": parse_object_id(integrationId, "integrationId"),
        "is_deleted": False,
    })

    if not integ:
        return None

    return {
        "id": str(integ["_id"]),
        "name": integ["name"],
        "description": integ.get("description"),
        "createdBy": str(integ["created_by"]),
        "createdAt": integ["created_at"].isoformat(),
    }

### get integration of particular user #####
@query.field("userIntegrations")
@requires_auth
async def resolve_user_integrations(_, info, userId):
    db = info.context["db"]

    user_oid = parse_object_id(userId, "userId")

    # Validate user exists
    user = await db.users.find_one({
        "_id": user_oid, "is_active": True
    })
    if not user:
        return ("user is either non-existent or inactive")

    integrations = []

    cursor = db.user_integrations.find({
        "user_id": user_oid
    })
    async for mapping in cursor:
        integ = await db.integrations.find_one({
            "_id": mapping["integration_id"],
            "is_deleted": False,
        })
        if integ:
            integrations.append({
                "id": str(integ["_id"]),
                "name": integ["name"],
                "description": integ.get("description"),
                "createdBy": str(integ["created_by"]),
                "createdAt": integ["created_at"].isoformat(),
            })

    return integrations