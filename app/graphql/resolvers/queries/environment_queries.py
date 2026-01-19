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




##### GET ENVIRONMENT BY ID ######
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
