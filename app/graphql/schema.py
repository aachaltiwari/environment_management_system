from ariadne.asgi import GraphQL
from app.graphql.context import get_context_value
from ariadne import load_schema_from_path, make_executable_schema
from app.graphql.resolvers.query import query
from app.graphql.resolvers.mutation import mutation

type_defs = load_schema_from_path("app/graphql/schema.graphql") 

schema = make_executable_schema(
    type_defs,
    query,
    mutation,
)


graphql_app = GraphQL(
    schema,
    context_value=get_context_value,
    debug=True, 
)
