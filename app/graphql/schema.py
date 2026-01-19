from ariadne.asgi import GraphQL
from app.graphql.context import get_context_value
from ariadne import ScalarType, load_schema_from_path, make_executable_schema
from app.graphql.resolvers import queries, mutations

type_defs = load_schema_from_path("app/graphql/schema.graphql") 

json_scalar = ScalarType("JSON")

@json_scalar.serializer
def serialize_json(value):
    return value

@json_scalar.value_parser
def parse_json_value(value):
    return value

schema = make_executable_schema(
    type_defs,
    queries,
    mutations, 
    json_scalar
)


graphql_app = GraphQL(
    schema,
    context_value=get_context_value,
    debug=True, 
)
