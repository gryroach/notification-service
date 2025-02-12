# stdlib
from dataclasses import dataclass
from enum import Enum

# project
from enums.db import EventType


@dataclass
class QueueConfig:
    queue_name: str
    ttl: int


class RabbitMQQueues(Enum):
    HIGH = QueueConfig("notifications.high", ttl=3600 * 1000)  # 1 hour
    MEDIUM = QueueConfig("notifications.medium", ttl=3600 * 2 * 1000)  # 2 hours
    LOW = QueueConfig("notifications.low", ttl=3600 * 3 * 1000)  # 3 hours

    @classmethod
    def list(cls) -> list[QueueConfig]:
        return [c.value for c in cls]


EVENT_TO_QUEUE_MAPPING = {
    EventType.USER_REGISTRATION: RabbitMQQueues.HIGH,
    EventType.NEW_MOVIE: RabbitMQQueues.LOW,
    EventType.CUSTOM: RabbitMQQueues.MEDIUM,
}


def get_queue_for_event(event_type: EventType) -> QueueConfig:
    """Возвращает очередь RabbitMQ, соответствующую типу события."""
    return EVENT_TO_QUEUE_MAPPING.get(event_type, RabbitMQQueues.MEDIUM).value
