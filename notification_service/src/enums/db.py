# stdlib
import enum


class NotificationType(str, enum.Enum):
    """Типы уведомлений, поддерживаемые системой."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class EventType(str, enum.Enum):
    """Типы событий, на которые система может реагировать."""

    USER_REGISTRATION = "user_registration"
    NEW_MOVIE = "new_movie"
    CUSTOM = "custom"
