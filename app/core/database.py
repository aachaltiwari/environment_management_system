from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def connect_mongo(app):
    client = AsyncIOMotorClient(settings.mongo_uri)
    app.state.mongo_client = client
    app.state.db = client[settings.mongo_db]
    print("MongoDB connected")


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

async def close_mongo(app):
    client = getattr(app.state, "mongo_client", None)
    if client:
        client.close()
        print("MongoDB disconnected")
