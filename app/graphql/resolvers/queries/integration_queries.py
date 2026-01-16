from ariadne import QueryType
from graphql import GraphQLError
from app.graphql.decorators import requires_auth
from app.graphql.errors import InternalServerError
from app.services import integration_service
from app.utils.objectid import parse_object_id

query = QueryType()

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

