from functools import wraps
from app.graphql.errors import AuthenticationError, AuthorizationError
from app.models.user import UserRole as Role
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