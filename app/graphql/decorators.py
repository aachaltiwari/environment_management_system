from functools import wraps
from app.graphql.errors import AuthenticationError, AuthorizationError, UserInputError
from app.permissions.integration import can_manupulate_integration
from app.permissions.user import can_manage_users

from app.permissions.environment import can_manipulate_environment
from app.utils.objectid import parse_object_id

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




def requires_environment_manipulation(resolver):
    @wraps(resolver)
    async def wrapper(parent, info, integrationId, **kwargs):
        user = info.context.get("user")
        db = info.context["db"]

        if not user:
            raise AuthenticationError("Authentication required")

        if not user.get("is_active", False):
            raise AuthenticationError("User account is inactive")

        integration_oid = parse_object_id(integrationId, "integrationId")

        integration = await db.integrations.find_one({
            "_id": integration_oid,
            "is_deleted": False,
        })

        if not integration:
            raise UserInputError(
                "Integration does not exist or is deleted"
            )

        # Check assignment
        mapping = await db.user_integrations.find_one({
            "user_id": user["_id"],
            "integration_id": integration_oid,
        })

        is_assigned = mapping is not None

        allowed = can_manipulate_environment(
            user,
            is_assigned=is_assigned,
        )

        if not allowed:
            raise AuthorizationError(
                "You do not have permission to modify environments"
            )

        return await resolver(
            parent,
            info,
            integrationId=integrationId,
            **kwargs
        )

    return wrapper
