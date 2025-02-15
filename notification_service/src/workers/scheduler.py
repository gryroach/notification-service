# stdlib
from datetime import UTC, datetime

# thirdparty
import orjson
from arq.connections import RedisSettings

# project
from core.config import settings
from db.db import get_session
from enums.db import get_priority_for_event
from enums.rabbitmq import get_queue_for_event
from services.notification_state import NotificationStateService
from services.subscriber_resolver import SubscriberResolver
from workers.base_worker import BaseTask, shutdown, startup


async def send_periodic_notifications(ctx: dict) -> None:
    current_time = datetime.now(UTC)
    resolver = SubscriberResolver()

    async for session in get_session():
        state_service = NotificationStateService(session)
        notifications = await state_service.get_pending_periodic(current_time)

        for notification in notifications:
            async for subscribers_batch in resolver.resolve(
                query_type=notification.subscriber_query_type,
                params=notification.subscriber_query_params,
                batch_size=100,
            ):
                message_body = {
                    "template_id": str(notification.template_id),
                    "context": notification.context,
                    "subscribers": subscribers_batch,
                    "event_type": notification.event_type,
                    "channel_type": notification.channel_type,
                    "notification_id": str(notification.id),
                }

                queue = get_queue_for_event(notification.event_type)
                priority = get_priority_for_event(notification.event_type)

                await ctx["rabbitmq"].send_message(
                    queue_name=queue.queue_name,
                    message_body=orjson.dumps(message_body),
                    priority=priority,
                )

            await state_service.update_periodic_run_time(notification.id, current_time)


async def send_scheduled_notifications(ctx: dict) -> None:
    current_time = datetime.now(UTC)
    resolver = SubscriberResolver()

    async for session in get_session():
        state_service = NotificationStateService(session)
        notifications = await state_service.get_pending_scheduled(
            current_time,
            batch_size=settings.scheduled_batch_size,
        )

        for notification in notifications:
            async for subscribers_batch in resolver.resolve(
                query_type=notification.subscriber_query_type,
                params=notification.subscriber_query_params,
                batch_size=100,
            ):
                message_body = {
                    "template_id": str(notification.template_id),
                    "context": notification.context,
                    "subscribers": subscribers_batch,
                    "event_type": notification.event_type,
                    "channel_type": notification.channel_type,
                    "notification_id": str(notification.id),
                }

                queue = get_queue_for_event(notification.event_type)
                priority = get_priority_for_event(notification.event_type)

                await ctx["rabbitmq"].send_message(
                    queue_name=queue.queue_name,
                    message_body=orjson.dumps(message_body),
                    priority=priority,
                )

            await state_service.mark_scheduled_sent(notification.id)


tasks = [
    BaseTask(
        name="periodic_notifications",
        function="src.workers.scheduler.send_periodic_notifications",
        coroutine=send_periodic_notifications,
        cron_schedule=settings.periodic_schedule,
    ),
    BaseTask(
        name="scheduled_notifications",
        function="src.workers.scheduler.send_scheduled_notifications",
        coroutine=send_scheduled_notifications,
        cron_schedule=settings.scheduled_schedule,
    ),
]

scheduler_settings = {
    "functions": [task.function for task in tasks],
    "cron_jobs": [task.as_cron_job() for task in tasks],
    "redis_settings": RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
        database=settings.redis_db,
    ),
    "queue_name": "scheduler_queue",
    "max_jobs": settings.arq_max_jobs,
    "job_timeout": settings.arq_job_timeout,
    "keep_result": settings.arq_job_keep_result,
    "on_startup": startup,
    "on_shutdown": shutdown,
}
