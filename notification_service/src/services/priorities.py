# stdlib
from dataclasses import dataclass

# Константа для максимального приоритета сообщения
MAX_PRIORITY = 5


@dataclass
class PriorityLevels:
    max_priority: int
    min_priority: int
    avg_priority: int

    @classmethod
    def from_max_priority(cls, max_priority: int) -> "PriorityLevels":
        """Создает объект PriorityLevels на основе максимального приоритета."""
        min_priority = 1
        avg_priority = (max_priority + min_priority) // 2
        return cls(
            max_priority=max_priority,
            min_priority=min_priority,
            avg_priority=avg_priority,
        )


priority_levels = PriorityLevels.from_max_priority(MAX_PRIORITY)
