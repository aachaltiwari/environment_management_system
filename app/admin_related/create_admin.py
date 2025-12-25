import asyncio

from app.core import database
from app.core.security import hash_password
from app.models.user import UserRole

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"   # keep literal for now


async def create_admin():
    await database.connect_mongo()

    print("DEBUG password bytes:", len(ADMIN_PASSWORD.encode("utf-8")))

    existing_admin = await database.db.users.find_one(
        {"role": UserRole.ADMIN}
    )

    if existing_admin:
        print("Admin already exists")
        await database.close_mongo()
        return

    await database.db.users.insert_one({
        "email": ADMIN_EMAIL,
        "name": "System Admin",
        "role": UserRole.ADMIN,
        "password_hash": hash_password(ADMIN_PASSWORD),
        "is_active": True,
    })

    print("Admin created")
    await database.close_mongo()


if __name__ == "__main__":
    asyncio.run(create_admin())
