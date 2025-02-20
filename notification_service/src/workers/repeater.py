# stdlib
import logging
from typing import TYPE_CHECKING

# thirdparty
from arq.connections import RedisSettings
from redis.asyncio import Redis

# project
from core.config import settings
from enums.rabbitmq import RabbitMQQueues
from workers.base_worker import BaseTask, shutdown, startup

if TYPE_CHECKING:
    # project
    from services.rabbitmq import RabbitMQService

logger = logging.getLogger(__name__)


async def process_redis_messages(ctx: dict) -> None:
    redis = Redis.from_url(settings.redis_url)
    rabbitmq_service: RabbitMQService = ctx["rabbitmq"]

    for queue in RabbitMQQueues:
        queue_name = queue.value.queue_name
        for _ in range(settings.repeater_batch_size):
            message = await redis.lpop(queue_name)
            if not message:
                break

            try:
                await rabbitmq_service.send_message(queue_name=queue_name, message_body=message, priority=1)
                logger.info(f"Message successfully requeued to {queue_name}")
            except Exception as e:
                logger.error(f"Failed to requeue message to {queue_name}: {e}")
                await redis.rpush(queue_name, message)
                break


tasks = [
    BaseTask(
        name="redis_repeater",
        function="src.workers.repeater.process_redis_messages",
        coroutine=process_redis_messages,
        cron_schedule=settings.repeater_schedule,
    )
]

scheduler_settings = {
    "functions": [task.function for task in tasks],
    "cron_jobs": [task.as_cron_job() for task in tasks],
    "redis_settings": RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
        database=settings.redis_db,
    ),
    "queue_name": "repeater_queue",
    "max_jobs": settings.arq_max_jobs,
    "job_timeout": settings.arq_job_timeout,
    "keep_result": settings.arq_job_keep_result,
    "on_startup": startup,
    "on_shutdown": shutdown,
}
