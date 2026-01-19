from ariadne import MutationType
from app.graphql.decorators import requires_admin
from app.services.environment_type_service import create_environment_type
from app.graphql.errors import InternalServerError
import graphql

mutation = MutationType()

##### CREATE ENVIRONMENT TYPE ######
@mutation.field("createEnvironmentType")
@requires_admin
async def resolve_create_environment_type(_, info, input):
    try:
        return await create_environment_type(
            db=info.context["db"],
            user=info.context["user"],
            name=input["name"],
        )
    except graphql.GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred during environment type creation") from e