from ariadne import MutationType
from bson import ObjectId

from app.graphql.decorators import requires_admin
from app.graphql.errors import InternalServerError  
from app.services import user_service
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
    except Exception as e:
        raise InternalServerError("An error occurred during login") from e

# -------------------------
# REFRESH TOKEN
# -------------------------

@mutation.field("refreshToken")
async def resolve_refresh(_, info, refreshToken):
    return await user_service.refresh_access_token(
        info.context["db"],
        refreshToken,
    )


# -------------------------
# CREATE USER
# -------------------------

@mutation.field("createUser")
@requires_admin
async def resolve_create_user(_, info, input):
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


# -------------------------
# UPDATE USER
# -------------------------

@mutation.field("updateUser")
@requires_admin
async def resolve_update_user(_, info, userId, input):
    user_oid = parse_object_id(userId, "userId")

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


##### create integration mutation #####
@mutation.field("createIntegration")
@requires_integration_manupulation
async def resolve_create_integration(_, info, input):
    return await integration_service.create_integration(
        db=info.context["db"],
        user=info.context["user"],
        input=input,
    )


@mutation.field("assignUserToIntegration")
@requires_integration_manupulation
async def resolve_assign_user(_, info, integrationId, userId):
    return await integration_service.assign_user_to_integration(
        db=info.context["db"],
        integrationId=integrationId,
        userId=userId,
    )


@mutation.field("updateIntegration")
@requires_integration_manupulation
async def resolve_update_integration(_, info, integrationId, input):
    return await integration_service.update_integration(
        db=info.context["db"],
        integrationId=integrationId,
        input=input,
    )


@mutation.field("deleteIntegration")
@requires_integration_manupulation
async def resolve_delete_integration(_, info, integrationId):
    return await integration_service.soft_delete_integration(
        db=info.context["db"],
        integrationId=integrationId,
    )


@mutation.field("removeUserFromIntegration")
@requires_integration_manupulation
async def resolve_remove_user(_, info, integrationId, userId):
    return await integration_service.remove_user_from_integration(
        db=info.context["db"],
        integrationId=integrationId,
        userId=userId,
    )

