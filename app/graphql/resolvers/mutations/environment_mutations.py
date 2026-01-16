from ariadne import MutationType
from graphql import GraphQLError
from app.graphql.decorators import requires_environment_manipulation
from app.graphql.errors import InternalServerError
from app.services.environment_service import create_environment, update_environment, delete_environment


mutation = MutationType()


##### create environment mutation #####
@mutation.field("createEnvironment")
@requires_environment_manipulation
async def resolve_create_environment(_, info, integrationId, input):
    try:
        env = await create_environment(
            info.context["db"],
            info.context["user"],
            integrationId,
            input,
        )

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
        raise InternalServerError("An error occurred during environment creation") from e



##### update environment mutation #####
@mutation.field("updateEnvironment")
@requires_environment_manipulation
async def resolve_update_environment(_, info, integrationId, environmentId, input):
    try:
        env = await update_environment(
            info.context["db"],
            info.context["user"],
            integrationId,
            environmentId,
            input,
        )

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
        raise InternalServerError("An error occurred during environment update") from e




##### delete environment mutation #####
@mutation.field("deleteEnvironment")
@requires_environment_manipulation
async def resolve_delete_environment(_, info, integrationId, environmentId):
    try:
        return await delete_environment(info.context["db"], integrationId, environmentId)
    
    except GraphQLError:
        raise

    except Exception as e:
        raise InternalServerError("An error occurred during environment deletion") from e   
   