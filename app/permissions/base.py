from app.models.user import UserRole


def is_admin(user: dict) -> bool:
    return user["role"] == UserRole.ADMIN.value


def is_team_lead(user: dict) -> bool:
    return user["role"] == UserRole.TEAM_LEAD.value


def is_active_user(user: dict) -> bool:
    return user and user.get("is_active", False)
