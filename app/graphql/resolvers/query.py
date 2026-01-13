from ariadne import QueryType
from app.graphql.decorators import requires_auth
from app.services import user_service
from app.services import integration_service
from app.utils.objectid import parse_object_id

query = QueryType()


@query.field("me")
@requires_auth
async def resolve_me(_, info):
    user = await user_service.get_current_user(
        info.context["user"]
    )

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
    }


@query.field("users")
async def resolve_users(_, info):
    users = await user_service.list_active_users(
        info.context["db"]
    )

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



# -------------------------
# ALL INTEGRATIONS
# -------------------------

@query.field("integrations")
@requires_auth
async def resolve_integrations(_, info):
    return await integration_service.get_integrations(
        info.context["db"]
    )


# -------------------------
# SINGLE INTEGRATION
# -------------------------

@query.field("integration")
@requires_auth
async def resolve_integration(_, info, integrationId):
    integration_oid = parse_object_id(
        integrationId, "integrationId"
    )

    return await integration_service.get_integration_by_id(
        info.context["db"],
        integration_oid,
    )


# -------------------------
# USER → INTEGRATIONS
# -------------------------

@query.field("userIntegrations")
@requires_auth
async def resolve_user_integrations(_, info, userId):
    user_oid = parse_object_id(userId, "userId")

    return await integration_service.get_user_integrations(
        info.context["db"],
        user_oid,
    )