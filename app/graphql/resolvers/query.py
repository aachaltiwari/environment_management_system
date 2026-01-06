from ariadne import QueryType
from bson import ObjectId
from app.graphql.decorators import requires_admin, requires_auth

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

    users = await db.users.find().to_list(length=None)

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

    cursor = db.integrations.find()
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

    integ = await db.integrations.find_one({
        "_id": ObjectId(integrationId)
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
