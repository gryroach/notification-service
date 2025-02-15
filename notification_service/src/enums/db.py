# stdlib
from enum import StrEnum

# project
from services.priorities import priority_levels


class ChannelType(StrEnum):
    """Типы уведомлений, поддерживаемые системой."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class EventType(StrEnum):
    """Типы событий, на которые система может реагировать."""

    USER_REGISTRATION = "user_registration"
    NEW_MOVIE = "new_movie"
    CUSTOM = "custom"


EVENT_TO_PRIORITY_MAPPING: dict[EventType, int] = {
    EventType.USER_REGISTRATION: priority_levels.max_priority,
    EventType.NEW_MOVIE: priority_levels.min_priority,
    EventType.CUSTOM: priority_levels.avg_priority,
}


def get_priority_for_event(event_type: EventType) -> int:
    """Возвращает очередь RabbitMQ, соответствующую типу события."""
    return EVENT_TO_PRIORITY_MAPPING.get(event_type, priority_levels.avg_priority)
