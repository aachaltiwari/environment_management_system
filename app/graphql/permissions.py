from functools import wraps
from app.graphql.errors import AuthenticationError, AuthorizationError
from app.models.user import UserRole as Role


def requires_auth(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, **kwargs):
        if not info.context["user"]:
            raise AuthenticationError()
        return await resolver(parent, info, **kwargs)
    return wrapper


def requires_role(role: Role):
    def decorator(resolver):
        @wraps(resolver)
        async def wrapper(parent, info, **kwargs):
            user = info.context["user"]
            if not user:
                raise AuthenticationError()
            if user["role"] != role.value:
                raise AuthorizationError(f"{role.value} role required")
            return await resolver(parent, info, **kwargs)
        return wrapper
    return decorator
