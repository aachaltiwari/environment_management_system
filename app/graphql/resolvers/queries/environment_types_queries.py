from ariadne import QueryType
from app.graphql.decorators import requires_auth
from app.services.environment_type_service import list_environment_types
from app.graphql.errors import InternalServerError
import graphql

query = QueryType()


@query.field("environmentTypes")
@requires_auth
async def resolve_environment_types(_, info):
    try:
        return await list_environment_types(info.context["db"])
    except graphql.GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching environment types") from e