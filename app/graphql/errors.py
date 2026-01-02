from graphql import GraphQLError


class AuthenticationError(GraphQLError):
    def __init__(self, message="Authentication failed"):
        super().__init__(
            message,
            extensions={"code": "UNAUTHENTICATED"},
        )


class AuthorizationError(GraphQLError):
    def __init__(self, message="Not authorized"):
        super().__init__(
            message,
            extensions={"code": "FORBIDDEN"},
        )


class UserInputError(GraphQLError):
    def __init__(self, message):
        super().__init__(
            message,
            extensions={"code": "BAD_USER_INPUT"},
        )