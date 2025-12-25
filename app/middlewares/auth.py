from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import JWTError
from app.core.security import decode_token
from app.core.database import db


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        public_paths = {"/auth/login", "/health"}

        if request.url.path in public_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
        except JWTError:
            return JSONResponse({"detail": "Invalid token"}, status_code=401)

        user = await db.users.find_one({"_id": user_id})

        if not user:
            return JSONResponse({"detail": "User not found"}, status_code=401)

        request.state.user = user
        return await call_next(request)
