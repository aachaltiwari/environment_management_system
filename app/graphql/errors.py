from graphql import GraphQLError


class AuthenticationError(GraphQLError):
    def __init__(self):
        super().__init__(
            "Authentication required",
            extensions={"code": "UNAUTHENTICATED"},
        )


class AuthorizationError(GraphQLError):
    def __init__(self, message="Permission denied"):
        super().__init__(
            message,
            extensions={"code": "FORBIDDEN"},
        )
