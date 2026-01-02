from ariadne import MutationType
from bson import ObjectId
from jose import JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.graphql.decorators import requires_admin
from app.models.user import UserRole
from app.graphql.errors import UserInputError, AuthenticationError

mutation = MutationType()

##### login mutation #####

@mutation.field("login")
async def resolve_login(_, info, email, password):
    db = info.context["db"]

    user = await db.users.find_one({"email": email})

    if not user or not verify_password(password, user["password_hash"]):
        raise AuthenticationError("Invalid email or password")

    if not user.get("is_active", False):
        raise AuthenticationError("User account is inactive")

    return {
        "accessToken": create_access_token(
            str(user["_id"]), user["role"]
        ),
        "refreshToken": create_refresh_token(
            str(user["_id"])
        ),
    }

##### refreshToken mutation #####

@mutation.field("refreshToken")
async def resolve_refresh(_, info, refreshToken):
    try:
        payload = decode_token(refreshToken)
    except JWTError:
        raise AuthenticationError("Invalid refresh token")

    if payload.get("token_type") != "refresh":
        raise AuthenticationError("Invalid token type")

    user_id = payload.get("sub")
    db = info.context["db"]

    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user or not user.get("is_active", False):
        raise AuthenticationError("User not found or inactive")

    return {
        "accessToken": create_access_token(
            str(user["_id"]), user["role"]
        )
    }


##### createUser mutation #####

@mutation.field("createUser")
@requires_admin
async def resolve_create_user(_, info, input):
    db = info.context["db"]

    email = input["email"].lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise UserInputError("User with this email already exists")

    if input["role"] not in UserRole.__members__:
        raise UserInputError("Invalid role")

    user = {
        "email": email,
        "name": input["name"],
        "role": input["role"],
        "password_hash": hash_password(input["password"]),
        "is_active": True,
    }

    result = await db.users.insert_one(user)

    return {
        "id": str(result.inserted_id),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "isActive": user["is_active"],
    }


##### setUserActive mutation #####

@mutation.field("setUserActive")
@requires_admin
async def resolve_set_user_active(_, info, userId, isActive):
    db = info.context["db"]

    result = await db.users.find_one_and_update(
        {"_id": ObjectId(userId)},
        {"$set": {"is_active": isActive}},
        return_document=True,
    )

    if not result:
        raise ValueError("User not found")

    return {
        "id": str(result["_id"]),
        "email": result["email"],
        "name": result["name"],
        "role": result["role"],
        "isActive": result["is_active"],
    }
