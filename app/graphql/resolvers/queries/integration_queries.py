from ariadne import QueryType
from graphql import GraphQLError
from app.graphql.decorators import requires_auth
from app.graphql.errors import InternalServerError
from app.services import integration_service
from app.utils.objectid import parse_object_id

query = QueryType()


#### lIST INTEGRATIONS ######
@query.field("integrations")
@requires_auth
async def resolve_integrations(
    _,
    info,
    page=1,
    pageSize=10,
    search=None,
    assignedUserId=None,
):
    try:
        assigned_user_oid = (
            parse_object_id(assignedUserId, "assignedUserId")
            if assignedUserId else None
        )

        return await integration_service.list_integrations(
            db=info.context["db"],
            page=page,
            pageSize=pageSize,
            search=search,
            assigned_user_id=assigned_user_oid,
        )

    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("Error fetching integrations") from e

    



##### GET INTEGRATION BY ID ######
@query.field("integration")
@requires_auth
async def resolve_integration(_, info, integrationId):
    
    try:
        integration_oid = parse_object_id(
        integrationId, "integrationId"
    )
        return await integration_service.get_integration_by_id(
            info.context["db"],
            integration_oid,
        )
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching integration") from e
    



##### GET USER INTEGRATIONS ######
@query.field("userIntegrations")
@requires_auth
async def resolve_user_integrations(_, info, userId):
    
    try:
        user_oid = parse_object_id(userId, "userId")
        return await integration_service.get_user_integrations(
            info.context["db"],
            user_oid,
        )
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching user integrations") from e

