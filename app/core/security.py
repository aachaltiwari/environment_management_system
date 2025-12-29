from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from jose import JWTError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


### Password Hashing Function
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


### JWT Token Functions

# Create Access Token
def create_access_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "token_type": "access",
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


# Create Refresh Token
def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "token_type": "refresh",
        "exp": datetime.utcnow()
        + timedelta(days=settings.jwt_refresh_token_expire_days),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )



# Decode Refresh Token
def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
