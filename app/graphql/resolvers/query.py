from ariadne import QueryType
from app.graphql.permissions import requires_auth

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

