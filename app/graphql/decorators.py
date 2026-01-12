from functools import wraps
from app.graphql.errors import AuthenticationError, AuthorizationError
from app.permissions.integration import can_manupulate_integration
from app.permissions.user import can_manage_users

def requires_auth(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, **kwargs):
        user = info.context.get("user")

        if not user:
            raise AuthenticationError("Authentication required")

        if not user.get("is_active"):
            raise AuthenticationError("User account is inactive")

        return await resolver(parent, info, **kwargs)

    return wrapper




def requires_admin(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, **kwargs):
        user = info.context.get("user")

        if not user:
            raise AuthenticationError("Authentication required")

        if not user.get("is_active"):
            raise AuthenticationError("User account is inactive")

        if not can_manage_users(user):
            raise AuthorizationError("Admin access required")

        return await resolver(parent, info, **kwargs)

    return wrapper



def requires_integration_manupulation(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, **kwargs):
        user = info.context["user"]

        if not user:
            raise AuthenticationError()
        
        if not user.get("is_active"):
            raise AuthenticationError("User account is inactive")


        allowed = await can_manupulate_integration(user)
        if not allowed:
            raise AuthorizationError(
                "Only Team Lead or Admin can create integration"
            )

        return await resolver(parent, info, **kwargs)

    return wrapper
