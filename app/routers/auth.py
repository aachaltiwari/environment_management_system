from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from app.schemas.user import LoginRequest
from app.core.security import verify_password, create_access_token


async def login(request):
    data = await request.json()
    login_data = LoginRequest(**data)

    db = request.app.state.db
    user = await db.users.find_one({"email": login_data.email})

    if not user:
        return JSONResponse({"detail": "Invalid credentials"}, status_code=401)

    if not verify_password(login_data.password, user["password_hash"]):
        return JSONResponse({"detail": "Invalid credentials"}, status_code=401)

    token = create_access_token({
        "sub": str(user["_id"]),
        "role": user["role"]
    })

    return JSONResponse({
        "access_token": token,
        "token_type": "bearer"
    })


routes = [
    Route("/auth/login", login, methods=["POST"])
]
