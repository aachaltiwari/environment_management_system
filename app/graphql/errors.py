from graphql import GraphQLError
from enum import StrEnum


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


class UserInputError(GraphQLError):
    def __init__(self, message):
        super().__init__(
            message,
            extensions={"code": "BAD_USER_INPUT"},
        )