from ariadne import MutationType
from graphql import GraphQLError
from app.graphql.decorators import requires_admin 
from app.graphql.errors import InternalServerError
from app.services import user_service
from app.utils.objectid import parse_object_id

mutation = MutationType()



##### LOGIN USER ######
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



##### REFRESH ACCESS TOKEN ######
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



##### CREATE USER ######
@mutation.field("createUser")
@requires_admin
async def resolve_create_user(_, info, input):
    try:
        return await user_service.create_user(
            info.context["db"],
            input,
        )
    
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred during user creation") from e



##### UPDATE USER ######
@mutation.field("updateUser")
@requires_admin
async def resolve_update_user(_, info, userId, input):
    
    try:
        user_oid = parse_object_id(userId, "userId")
        return await user_service.update_user(
            info.context["db"],
            user_oid,
            input,
        )
    
    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred during user update") from e
