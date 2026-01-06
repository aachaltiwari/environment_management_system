from bson import ObjectId
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError

from app.core.security import decode_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.state.user = None

        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return await call_next(request)

        token = auth.split(" ", 1)[1]

        try:
            payload = decode_token(token)
        except JWTError:
            return await call_next(request)

        if payload.get("token_type") != "access":
            return await call_next(request)

        user_id = payload.get("sub")
        if not user_id:
            return await call_next(request)

        user = await request.app.state.db.users.find_one(
            {"_id": ObjectId(user_id)}
        )

        if user:
            request.state.user = user

        return await call_next(request)


# from fastapi import Request
# from bson import ObjectId
# from jose import JWTError
# from app.core.security import decode_token


# class AuthMiddleware:
#     def __init__(self, app):
#         self.app = app

#     async def __call__(self, scope, receive, send):
#         # Only handle HTTP requests
#         if scope["type"] != "http":
#             await self.app(scope, receive, send)
#             return

#         # Wrap the ASGI scope in a FastAPI Request object
#         request = Request(scope, receive=receive)

#         # Default: no user
#         request.state.user = None

#         auth = request.headers.get("Authorization")
#         if auth and auth.startswith("Bearer "):
#             token = auth.split(" ", 1)[1]

#             try:
#                 payload = decode_token(token)
#                 if payload.get("token_type") == "access":
#                     user_id = payload.get("sub")
#                     if user_id:
#                         user = await request.app.state.db.users.find_one(
#                             {"_id": ObjectId(user_id)}
#                         )
#                         if user:
#                             request.state.user = user
#             except JWTError:
#                 # Invalid token → leave user as None
#                 pass

#         # Call next ASGI app in the chain
#         await self.app(scope, receive, send)
