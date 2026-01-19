from ariadne import QueryType
from graphql import GraphQLError
from app.graphql.decorators import requires_auth
from app.graphql.errors import InternalServerError
from app.services import user_service

query = QueryType()


###### CURRENT AUTHENTICATED USER ######
@query.field("me")
@requires_auth
async def resolve_me(_, info):
    try:
        return await user_service.get_current_user(
            info.context["user"]
        )

    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching current user") from e



####### LIST ACTIVE USERS ######
@query.field("users")
@requires_auth
async def resolve_users(_, info, page, pageSize, search=None):
    try:
        result = await user_service.list_active_users(
            db=info.context["db"],
            page=page,
            pageSize=pageSize,
            search=search,
        )

        return {
            "items": [
                {
                    "id": str(u["_id"]),
                    "email": u["email"],
                    "name": u["name"],
                    "role": u["role"],
                    "isActive": u["is_active"],
                }
                for u in result["items"]
            ],
            "page": result["page"],
            "pageSize": result["pageSize"],
            "totalItems": result["totalItems"],
            "totalPages": result["totalPages"],
        }

    except GraphQLError:
        raise
    except Exception as e:
        raise InternalServerError("An error occurred fetching users") from e