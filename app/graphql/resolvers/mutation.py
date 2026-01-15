from ariadne import MutationType
from bson import ObjectId
from graphql import GraphQLError

from app.graphql.decorators import requires_admin, requires_environment_manipulation
from app.graphql.errors import InternalServerError  
from app.services import user_service
from app.services.environment_service import create_environment, delete_environment, update_environment
from app.utils.objectid import parse_object_id

from ariadne import MutationType
from app.graphql.decorators import requires_integration_manupulation
from app.services import integration_service

mutation = MutationType()



# -------------------------
# LOGIN
# -------------------------

@mutation.field("login")
async def resolve_login(_, info, email, password):
    try:
        return await user_service.login_user(
            info.context["db"],
            email,
            password,
        )
    except GraphQLError:
        raise

    except Exception as e:
        raise InternalServerError("An error occurred during login") from e

# -------------------------
# REFRESH TOKEN
# -------------------------

@mutation.field("refreshToken")
async def resolve_refresh(_, info, refreshToken):
    try:
        return await user_service.refresh_access_token(
            info.context["db"],
            refreshToken,
        )
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred during token refresh") from e

# -------------------------
# CREATE USER
# -------------------------

@mutation.field("createUser")
@requires_admin
async def resolve_create_user(_, info, input):
    try:
        user = await user_service.create_user(
            info.context["db"],
            input,
        )
   
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "isActive": user["is_active"],
        }
    
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred during user creation") from e


# -------------------------
# UPDATE USER
# -------------------------

@mutation.field("updateUser")
@requires_admin
async def resolve_update_user(_, info, userId, input):
    user_oid = parse_object_id(userId, "userId")
    try:
        user = await user_service.update_user(
            info.context["db"],
            ObjectId(user_oid),
            input,
        )

        return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "isActive": user["is_active"],
    }
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred during user update") from e


##### create integration mutation #####
@mutation.field("createIntegration")
@requires_integration_manupulation
async def resolve_create_integration(_, info, input):
    try:
        return await integration_service.create_integration(
            db=info.context["db"],
            user=info.context["user"],
            input=input, )
        
    except GraphQLError:
        raise       
    except Exception as e:
        raise InternalServerError("An error occurred during integration creation") from e


@mutation.field("assignUserToIntegration")
@requires_integration_manupulation
async def resolve_assign_user(_, info, integrationId, userId):
    try:
        return await integration_service.assign_user_to_integration(
            db=info.context["db"],
            integrationId=integrationId,
            userId=userId,
        )
    except GraphQLError:
        raise       
    except Exception as e:
        raise InternalServerError("An error occurred during user assignment to integration") from e     



@mutation.field("updateIntegration")
@requires_integration_manupulation
async def resolve_update_integration(_, info, integrationId, input):
    try:
        return await integration_service.update_integration(
            db=info.context["db"],
            integrationId=integrationId,
            input=input,
        )
    except GraphQLError:
        raise       
    except Exception as e:
        raise InternalServerError("An error occurred during integration update") from e
    


@mutation.field("deleteIntegration")
@requires_integration_manupulation
async def resolve_delete_integration(_, info, integrationId):
    try:
        return await integration_service.soft_delete_integration(
            db=info.context["db"],
            integrationId=integrationId,
        )
    except GraphQLError:
        raise       
    except Exception as e:
        raise InternalServerError("An error occurred during integration deletion") from e
    


@mutation.field("removeUserFromIntegration")
@requires_integration_manupulation
async def resolve_remove_user(_, info, integrationId, userId):
    try:
        return await integration_service.remove_user_from_integration(
            db=info.context["db"],
            integrationId=integrationId,
            userId=userId,
        )
    except GraphQLError:
        raise       
    except Exception as e:
        raise InternalServerError("An error occurred during user removal from integration") from e




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
   