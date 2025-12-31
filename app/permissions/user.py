from app.permissions.base import is_admin


def can_manage_users(user: dict) -> bool:
    if not user:
        return False
    return is_admin(user)
