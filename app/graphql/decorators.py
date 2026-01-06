from functools import wraps
from app.graphql.errors import AuthenticationError, AuthorizationError
from app.models.user import UserRole as Role
from app.permissions.integration import can_create_integration, can_manage_integration
from app.permissions.user import can_manage_users

def requires_auth(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, **kwargs):
        if not info.context["user"]:
            raise AuthenticationError()
        return await resolver(parent, info, **kwargs)
    return wrapper




def requires_admin(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, **kwargs):
        user = info.context["user"]

        if not user:
            raise AuthenticationError()

        if not can_manage_users(user):
            raise AuthorizationError("Admin access required")

        return await resolver(parent, info, **kwargs)

    return wrapper



def requires_integration_creation(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, **kwargs):
        user = info.context["user"]

        if not user:
            raise AuthenticationError()

        allowed = await can_create_integration(user)
        if not allowed:
            raise AuthorizationError(
                "Only Team Lead or Admin can create integration"
            )

        return await resolver(parent, info, **kwargs)

    return wrapper



def requires_integration_management(resolver):
    async def wrapper(parent, info, integrationId, **kwargs):
        user = info.context["user"]
        db = info.context["db"]

        if not user:
            raise AuthenticationError()

        allowed = await can_manage_integration(db, user, integrationId)
        if not allowed:
            
            raise AuthorizationError("Integration access denied")

        return await resolver(parent, info, integrationId, **kwargs)

    return wrapper