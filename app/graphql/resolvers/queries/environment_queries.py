from ariadne import QueryType
from graphql import GraphQLError
from app.graphql.decorators import requires_auth
from app.graphql.errors import InternalServerError
from app.services.environment_service import get_environment, list_environments

query = QueryType()


##### LIST ENVIRONMENTS ######
@query.field("environments")
@requires_auth
async def resolve_environments(_, info, integrationId):
   
    try:
        db = info.context["db"]
        return await list_environments(db, integrationId)
    
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching environments") from e




##### GET ENVIRONMENT BY ID ######
@query.field("environment")
@requires_auth
async def resolve_environment(_, info, environmentId):
    
    try:
        db = info.context["db"]
        return await get_environment(db, environmentId) 
    
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching environment") from e
