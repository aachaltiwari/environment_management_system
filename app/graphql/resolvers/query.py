from ariadne import QueryType
from graphql import GraphQLError
from app.graphql.decorators import requires_auth
from app.graphql.errors import InternalServerError
from app.services import user_service
from app.services import integration_service
from app.services.environment_service import get_environment, list_environments
from app.utils.objectid import parse_object_id



query = QueryType()


@query.field("me")
@requires_auth
async def resolve_me(_, info):
    try:
        user = await user_service.get_current_user(
            info.context["user"]
        )

        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        }
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching current user") from e



@query.field("users")
async def resolve_users(_, info):
    try:
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
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching users") from e



# -------------------------
# ALL INTEGRATIONS
# -------------------------

@query.field("integrations")
@requires_auth
async def resolve_integrations(_, info):
    try:
        return await integration_service.get_integrations(
            info.context["db"]
        )
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching integrations") from e
    


# -------------------------
# SINGLE INTEGRATION
# -------------------------

@query.field("integration")
@requires_auth
async def resolve_integration(_, info, integrationId):
    integration_oid = parse_object_id(
        integrationId, "integrationId"
    )

    try:
        return await integration_service.get_integration_by_id(
            info.context["db"],
            integration_oid,
        )
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching integration") from e
    


# -------------------------
# USER → INTEGRATIONS
# -------------------------

@query.field("userIntegrations")
@requires_auth
async def resolve_user_integrations(_, info, userId):
    user_oid = parse_object_id(userId, "userId")
    try:
        return await integration_service.get_user_integrations(
            info.context["db"],
            user_oid,
        )
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching user integrations") from e


# ----------------------
# ALL ENVIRONMENTS FOR AN INTEGRATION
# ----------------------
@query.field("environments")
@requires_auth
async def resolve_environments(_, info, integrationId):
    db = info.context["db"]

    try:
        envs = await list_environments(db, integrationId)

        return [{
            "id": str(e["_id"]),
            "environmentType": e["environment_type"],
            "title": e["title"],
            "content": e["content"],
            "createdBy": str(e["created_by"]),
            "updatedBy": str(e["updated_by"]),
            "createdAt": e["created_at"].isoformat(),
            "updatedAt": e["updated_at"].isoformat(),
        } for e in envs]
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching environments") from e




# -------------------------
# SINGLE ENVIRONMENT
# -------------------------
@query.field("environment")
@requires_auth
async def resolve_environment(_, info, environmentId):
    db = info.context["db"]

    try:
        env = await get_environment(db, environmentId)
        if not env:
            return None

        return {
            "id": str(env["_id"]),
            "environmentType": env["environment_type"],
            "title": env["title"],
            "content": env["content"],
            "createdBy": str(env["created_by"]),
            "updatedBy": str(env["updated_by"]),
            "createdAt": env["created_at"].isoformat(),
            "updatedAt": env["updated_at"].isoformat(),
        }
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching environment") from e
