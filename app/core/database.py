from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

from loguru import logger


async def connect_mongo(app):
    client = AsyncIOMotorClient(settings.mongo_uri)
    app.state.mongo_client = client
    app.state.db = client[settings.mongo_db]
    logger.info("MongoDB connected")

    await app.state.db.users.create_index(
        [("email", 1)],
        unique=True)    


    await app.state.db.integrations.create_index(
        [("name", 1)],
        unique=True)
    

    await app.state.db.user_integrations.create_index(
    [
        ("user_id", 1),
        ("integration_id", 1),
    ],
    unique=True
    )


    await app.state.db.environment_types.create_index(
    [("name", 1)],
    unique=True
)
    
    await app.state.db.environments.create_index(
    [
        ("integration_id", 1),
        ("environment_type", 1),
    ],
    unique=True
)



async def close_mongo(app):
    client = getattr(app.state, "mongo_client", None)
    if client:
        client.close()
        logger.info("MongoDB disconnected")
        
