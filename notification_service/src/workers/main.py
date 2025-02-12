# stdlib
import asyncio
import logging
from logging import config as logging_config

# thirdparty
from arq.connections import ArqRedis
from arq.worker import Worker

# project
from core.logger import LOGGING
from workers.base import BaseWorker, BaseWorkerSettings
from workers.former import FormerWorker, FormerWorkerSettings
from workers.repeater import RepeaterWorker, RepeaterWorkerSettings
from workers.sheduler import SchedulerWorker, SchedulerWorkerSettings

logging_config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WORKER_SETTINGS_MAPPING: dict[str, type[BaseWorkerSettings] | None] = {
    "scheduler": SchedulerWorkerSettings,
    "repeater": RepeaterWorkerSettings,
    "former": FormerWorkerSettings,
}


def get_worker_class(worker_type: str) -> type[BaseWorker]:
    """Возвращает класс воркера по его типу."""
    worker_mapping = {
        "scheduler": SchedulerWorker,
        "repeater": RepeaterWorker,
        "former": FormerWorker,
    }
    if worker_type not in worker_mapping:
        raise ValueError(f"Unknown worker type: {worker_type}")
    return worker_mapping[worker_type]


async def run_worker(worker_type: str) -> None:
    """Запускает воркер указанного типа."""
    logger.debug(f"Starting worker of type: {worker_type}")
    worker_settings_cls: type[BaseWorkerSettings] | None = WORKER_SETTINGS_MAPPING.get(worker_type)
    if not worker_settings_cls:
        logger.error(f"Unknown worker type: {worker_type}")
        raise ValueError(f"Unknown worker type: {worker_type}")

    logger.debug("Creating worker settings from config")
    worker_settings = worker_settings_cls.from_settings()
    logger.debug(f"Worker settings: {worker_settings.__dict__}")

    redis_settings = worker_settings.redis_settings
    redis_pool = await ArqRedis.from_url(
        f"redis://{redis_settings['host']}:{redis_settings['port']}/{redis_settings['db']}"
    )

    logger.debug("Initializing worker")
    worker_class = get_worker_class(worker_type)
    context = await worker_class.get_context(worker_settings)
    worker = Worker(
        functions=worker_settings.functions,  # type: ignore
        cron_jobs=worker_settings.cron_jobs,
        on_startup=worker_settings.on_startup,
        on_shutdown=worker_settings.on_shutdown,
        queue_name=worker_settings.queue_name,
        redis_pool=redis_pool,
        max_jobs=worker_settings.max_jobs,
        ctx=context,
    )

    logger.info(f"Starting {worker_type} worker...")
    await worker.async_run()


def main() -> None:
    # stdlib
    import sys

    MIN_ARGS_COUNT = 2
    if len(sys.argv) < MIN_ARGS_COUNT:
        print("Usage: python -m workers.main <worker_type>")
        sys.exit(1)

    worker_type = sys.argv[1]
    asyncio.run(run_worker(worker_type))


if __name__ == "__main__":
    main()
