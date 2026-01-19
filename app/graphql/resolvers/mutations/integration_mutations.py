from ariadne import MutationType
from graphql import GraphQLError
from app.graphql.decorators import requires_integration_manupulation
from app.graphql.errors import InternalServerError
from app.services import integration_service

mutation = MutationType()


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



##### ASSIGN USER TO INTEGRATION ######
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



##### UPDATE INTEGRATION ######
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
    


##### SOFTDELETE INTEGRATION ######
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
    


##### REMOVE USER FROM INTEGRATION ######
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
