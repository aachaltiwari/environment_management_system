from bson import ObjectId
from bson.errors import InvalidId
from app.graphql.errors import UserInputError


def parse_object_id(value: str, field_name: str = "id") -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise UserInputError(f"Invalid {field_name}")
