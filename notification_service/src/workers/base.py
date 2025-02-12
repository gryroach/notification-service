# stdlib
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine, Sequence
from typing import Any, ClassVar, Protocol, TypedDict

# thirdparty
from arq.typing import StartupShutdown
from arq.worker import CronJob

# project
from core.config import settings
from services.rabbitmq import RabbitMQService


class WorkerSettingsBase(Protocol):
    """
    Базовый интерфейс для настроек воркера. Определяет обязательные атрибуты и методы,
    которые должны быть реализованы в конкретных настройках воркеров.
    """

    functions: Sequence[Callable[..., Coroutine[Any, Any, None]]] | None = None
    cron_jobs: Sequence[CronJob] | None = None
    on_startup: StartupShutdown | None = None
    on_shutdown: StartupShutdown | None = None
    queue_name: str
    redis_settings: dict[str, Any]
    max_jobs: int = 10


class WorkerContext(TypedDict):
    """
    Контекст выполнения воркера, содержащий зависимости и метаданные.
    Используется для передачи состояния между задачами воркера.
    """

    rabbitmq: RabbitMQService
    worker_type: str


class BaseWorkerSettings(WorkerSettingsBase, ABC):
    """
    Базовый класс для настроек воркеров. Реализует общую логику для всех типов воркеров,
    включая парсинг CRON-расписаний и создание настроек из конфигурации.
    """

    functions: Sequence[Callable[..., Coroutine[Any, Any, None]]] | None = None
    CRON_PARTS_COUNT: ClassVar[int] = 5
    WEEKDAYS: ClassVar[list[str]] = [
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
        "sun",
    ]

    def __init__(
        self,
        *,
        redis_settings: dict[str, Any],
        queue_name: str,
        max_jobs: int,
        job_timeout: int,
        keep_result: int,
    ):
        """
        Инициализирует настройки воркера.

        :param redis_settings: Настройки подключения к Redis.
        :param queue_name: Название очереди для задач.
        :param max_jobs: Максимальное количество одновременно выполняемых задач.
        :param job_timeout: Таймаут выполнения задачи в секундах.
        :param keep_result: Время хранения результата задачи в секундах.
        """
        self.redis_settings = redis_settings
        self.queue_name = queue_name
        self.max_jobs = max_jobs
        self.job_timeout = job_timeout
        self.keep_result = keep_result

    @property
    @abstractmethod
    def worker_type(self) -> str:
        """
        Возвращает тип воркера. Должен быть реализован в дочерних классах.

        :return: Строка с типом воркера (например, 'scheduler', 'repeater').
        """
        pass

    @classmethod
    def from_settings(cls) -> "BaseWorkerSettings":
        """
        Создает экземпляр настроек воркера на основе конфигурации приложения.

        :return: Экземпляр настроек воркера.
        """
        return cls(
            redis_settings={
                "host": settings.redis_host,
                "port": settings.redis_port,
                "db": settings.redis_db,
            },
            queue_name=f"{cls.worker_type}_queue",
            max_jobs=settings.arq_max_jobs,
            job_timeout=settings.arq_job_timeout,
            keep_result=settings.arq_job_keep_result,
        )

    @staticmethod
    def parse_cron_schedule(cron_str: str) -> dict[str, set[int] | int]:
        """
        Парсит строку CRON-расписания на отдельные компоненты.

        :param cron_str: Строка CRON-расписания.
        :return: Словарь с компонентами расписания.
        :raises ValueError: Если строка CRON имеет неверный формат.
        """
        parts = cron_str.split()
        if len(parts) != BaseWorkerSettings.CRON_PARTS_COUNT:
            raise ValueError(f"Invalid cron schedule: {cron_str}")

        minute_str, hour_str, day_str, month_str, weekday_str = parts

        # Преобразуем '*' в допустимые значения
        minute = list(range(0, 60)) if minute_str == "*" else [int(minute_str)]
        hour = list(range(0, 24)) if hour_str == "*" else [int(hour_str)]
        day = list(range(1, 32)) if day_str == "*" else [int(day_str)]
        month = list(range(1, 13)) if month_str == "*" else [int(month_str)]
        if weekday_str == "*":
            weekday = list(range(0, 7))
        elif weekday_str.isdigit():
            weekday = [int(weekday_str) % 7]
        else:
            weekday = [0]  # default value

        return {
            "minute": set(minute),
            "hour": set(hour),
            "day": set(day),
            "month": set(month),
            "weekday": set(weekday),
        }


class BaseWorker(ABC):
    """
    Базовый класс для всех воркеров. Реализует общую логику инициализации
    и управления жизненным циклом воркера.
    """

    CRON_PARTS_COUNT: ClassVar[int] = 5

    settings: BaseWorkerSettings

    def __init__(self) -> None:
        """
        Инициализирует контекст воркера с подключениями к БД и RabbitMQ.
        """
        self.ctx: WorkerContext = {
            "rabbitmq": RabbitMQService(),
            "worker_type": self.settings.worker_type,
        }

    @abstractmethod
    async def startup(self, ctx: WorkerContext) -> None:
        """
        Выполняет инициализацию воркера при старте. Должен быть реализован в дочерних классах.

        :param ctx: Контекст выполнения воркера.
        """
        pass

    @abstractmethod
    async def shutdown(self, ctx: WorkerContext) -> None:
        """
        Выполняет завершение работы воркера. Должен быть реализован в дочерних классах.

        :param ctx: Контекст выполнения воркера.
        """
        pass

    @classmethod
    async def get_context(cls, worker_settings: BaseWorkerSettings) -> dict[Any, Any] | None:
        """
        Создает контекст выполнения для воркера.

        :param worker_settings: Настройки воркера.
        :return: Контекст выполнения с подключениями и метаданными.
        """
        return {
            "rabbitmq": RabbitMQService(),
            "worker_type": worker_settings.worker_type,
        }
