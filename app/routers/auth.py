from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
# from app.schemas.user import LoginRequest
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.security import decode_token
from jose import JWTError
from bson import ObjectId


async def login(request):
    data = await request.json()
    login_data = LoginRequest(**data)

    db = request.app.state.db

    user = await db.users.find_one({"email": login_data.email})

    if not user or not verify_password(
        login_data.password, user["password_hash"]
    ):
        return JSONResponse(
            {"detail": "Invalid credentials"}, status_code=401
        )

    access_token = create_access_token(
        user_id=str(user["_id"]),
        role=user["role"],
    )

    refresh_token = create_refresh_token(
        user_id=str(user["_id"])
    )

    return JSONResponse(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )



#  new access token generation form refresh token
async def refresh_token(request):
    data = await request.json()
    token = data.get("refresh_token")

    if not token:
        return JSONResponse(
            {"detail": "Refresh token required"},
            status_code=400,
        )

    try:
        payload = decode_token(token)
    except JWTError:
        return JSONResponse(
            {"detail": "Invalid refresh token"},
            status_code=401,
        )

    if payload.get("token_type") != "refresh":
        return JSONResponse(
            {"detail": "Invalid token type"},
            status_code=401,
        )

    user_id = payload.get("sub")
    db = request.app.state.db


    user = await db.users.find_one(
    {"_id": ObjectId(user_id)})

    if not user or not user.get("is_active", False):
        return JSONResponse(
            {"detail": "User not found or inactive"},
            status_code=401,
        )

    new_access_token = create_access_token(
        user_id=str(user["_id"]),
        role=user["role"],
    )

    return JSONResponse(
        {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
    )


routes = [
    Route("/auth/login", login, methods=["POST"]),
    Route("/auth/refresh-token", refresh_token, methods=["POST"]),

]
