# stdlib
from enum import Enum

# project
from services.subscriber_resolver import SubscriberResolver


class SubscriberQueryEnum(Enum):
    """Динамический Enum, обновляемый на основе зарегистрированных fetcher-ов."""

    @classmethod
    def _update_enum(cls) -> None:
        """Обновляет значения Enum на основе _fetchers"""
        cls._member_map_.clear()
        for key in SubscriberResolver._fetchers:
            member = cls._value2member_map_.get(key)
            if member is None:
                member = cls(key)
            cls._member_map_[key] = member

    @classmethod
    def validate(cls, value: str) -> None:
        """Валидация значения на основе существующих значений Enum."""
        if value not in cls._member_map_:
            raise ValueError(f"Invalid query type: {value}. Allowed values: {list(cls._member_map_.keys())}")
