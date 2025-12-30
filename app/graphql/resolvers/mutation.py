from ariadne import MutationType
from bson import ObjectId
from jose import JWTError

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

mutation = MutationType()

@mutation.field("login")
async def resolve_login(_, info, email, password):                                  
    db = info.context["db"]

    user = await db.users.find_one({"email": email})

    if not user or not verify_password(password, user["password_hash"]):
        raise Exception("Invalid credentials")

    return {
        "accessToken": create_access_token(
            str(user["_id"]), user["role"]
        ),
        "refreshToken": create_refresh_token(
            str(user["_id"])
        ),
    }


@mutation.field("refreshToken")
async def resolve_refresh(_, info, refreshToken):
    try:
        payload = decode_token(refreshToken)
    except JWTError:
        raise Exception("Invalid refresh token")

    if payload.get("token_type") != "refresh":
        raise Exception("Invalid token type")

    user_id = payload.get("sub")
    db = info.context["db"]

    user = await db.users.find_one(
        {"_id": ObjectId(user_id)}
    )

    if not user or not user.get("is_active"):
        raise Exception("User not found or inactive")

    return {
        "accessToken": create_access_token(
            str(user["_id"]), user["role"]
        )
    }


