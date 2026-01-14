from app.models.user import UserRole


def can_manipulate_environment(user: dict, is_assigned: bool) -> bool:
    if not user:
        return False

    # Admin & Team Lead → always write
    if user["role"] in {
        UserRole.ADMIN.value,
        UserRole.TEAM_LEAD.value,
    }:
        return True

    # Developer → write only if assigned
    if user["role"] == UserRole.DEVELOPER.value and is_assigned:
        return True

    return False
