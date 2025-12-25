from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(alias="APP_NAME")
    debug: bool = Field(alias="DEBUG")

    mongo_uri: str = Field(alias="MONGO_URI")
    mongo_db: str = Field(alias="MONGO_DB")

    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: str = Field(alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        populate_by_name = True


settings = Settings()


