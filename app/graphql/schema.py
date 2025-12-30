from ariadne import make_executable_schema
from ariadne import QueryType, MutationType
from app.graphql.resolvers.query import query
from app.graphql.resolvers.mutation import mutation

type_defs = """
    type Query {
        me: User
    }

    type Mutation {
        login(email: String!, password: String!): AuthPayload!
        refreshToken(refreshToken: String!): AccessTokenPayload!
    }

    type User {
        id: ID!
        email: String!
        name: String!
        role: String!
    }

    type AuthPayload {
        accessToken: String!
        refreshToken: String!
    }

    type AccessTokenPayload {
        accessToken: String!
    }
"""

schema = make_executable_schema(
    type_defs,
    query,
    mutation,
)
