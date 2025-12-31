from ariadne import QueryType
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
@requires_admin
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
