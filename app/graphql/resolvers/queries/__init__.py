from ariadne import QueryType

from .user_queries import query as user_query
from .integration_queries import query as integration_query
from .environment_queries import query as environment_query
from .environment_types_queries import query as environment_types_query


query_resolvers = QueryType()

for q in [user_query, integration_query, environment_query, environment_types_query]:
    for name, resolver in q._resolvers.items():
        query_resolvers.set_field(name, resolver)