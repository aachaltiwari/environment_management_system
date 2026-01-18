from typing import List
from bson import ObjectId
from jose import JWTError
from pymongo.errors import DuplicateKeyError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import UserRole
from app.graphql.errors import UserInputError, AuthenticationError


###### services for user queries ######
async def get_current_user(user: dict) -> dict:
    """
    Returns current authenticated user
    """
    return user



from math import ceil
from typing import Optional

PAGE_SIZE = 10


async def list_active_users(
    db,
    page: int = 1,
    search: Optional[str] = None,
):
    if page < 1:
        page = 1

    query = {"is_active": True}

    # 🔍 Search by name (case-insensitive)
    if search:
        query["name"] = {
            "$regex": search,
            "$options": "i",
        }

    skip = (page - 1) * PAGE_SIZE

    cursor = (
        db.users
        .find(query)
        .skip(skip)
        .limit(PAGE_SIZE)
        .sort("name", 1)
    )

    users = await cursor.to_list(length=PAGE_SIZE)
    total_items = await db.users.count_documents(query)

    return {
        "items": users,
        "page": page,
        "pageSize": PAGE_SIZE,
        "totalItems": total_items,
        "totalPages": ceil(total_items / PAGE_SIZE) if total_items else 1,
    }





###### user services for mutations ######
# -------------------------
# AUTH
# -------------------------

async def login_user(db, email: str, password: str):
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


async def refresh_access_token(db, refresh_token: str):
    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise AuthenticationError("Invalid refresh token")

    if payload.get("token_type") != "refresh":
        raise AuthenticationError("Invalid token type")

    user_id = payload.get("sub")

    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user or not user.get("is_active", False):
        raise AuthenticationError("User not found or inactive")

    return {
        "accessToken": create_access_token(
            str(user["_id"]), user["role"]
        )
    }


# -------------------------
# USER MANAGEMENT
# -------------------------

async def create_user(db, input_data: dict):
    email = input_data["email"].lower()

    if await db.users.find_one({"email": email}):
        raise UserInputError("User with this email already exists")

    if input_data["role"] not in UserRole.__members__:
        raise UserInputError("Invalid role")

    user = {
        "email": email,
        "name": input_data["name"],
        "role": input_data["role"],
        "password_hash": hash_password(input_data["password"]),
        "is_active": True,
    }

    result = await db.users.insert_one(user)

    user["_id"] = result.inserted_id
    return user



async def update_user(db, user_oid: ObjectId, input_data: dict):
    update_data = {}

    if input_data.get("name") is not None:
        update_data["name"] = input_data["name"].strip()

    if input_data.get("role") is not None:
        if input_data["role"] not in UserRole.__members__:
            raise UserInputError("Invalid role")
        update_data["role"] = input_data["role"]

    if input_data.get("isActive") is not None:
        update_data["is_active"] = input_data["isActive"]

    if not update_data:
        raise UserInputError("No valid fields provided for update")

    result = await db.users.find_one_and_update(
        {"_id": user_oid},
        {"$set": update_data},
        return_document=True,
    )

    if not result:
        raise UserInputError("User not found")

    return result
