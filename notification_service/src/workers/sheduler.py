# stdlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine, Sequence

# thirdparty
import orjson
from arq import cron

# project
from core.config import settings
from db.db import get_session
from enums.db import EventType, get_priority_for_event
from enums.rabbitmq import get_queue_for_event
from services.notification_state import NotificationStateService
from workers.base import BaseWorker, BaseWorkerSettings, WorkerContext


class SchedulerWorkerSettings(BaseWorkerSettings):
    worker_type = "scheduler"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        periodic_schedule = self.parse_cron_schedule(settings.periodic_schedule)
        scheduled_schedule = self.parse_cron_schedule(settings.scheduled_schedule)

        self.cron_jobs = [
            cron(
                SchedulerWorker.send_periodic_notifications,  # type: ignore
                month=periodic_schedule.get("month"),
                day=periodic_schedule.get("day"),
                weekday=periodic_schedule.get("weekday"),
                hour=periodic_schedule.get("hour"),
                minute=periodic_schedule.get("minute"),
                unique=True,
            ),
            cron(
                SchedulerWorker.send_scheduled_notifications,  # type: ignore
                month=scheduled_schedule.get("month"),
                day=scheduled_schedule.get("day"),
                weekday=scheduled_schedule.get("weekday"),
                hour=scheduled_schedule.get("hour"),
                minute=scheduled_schedule.get("minute"),
                unique=True,
            ),
        ]

        self.functions: Sequence[Callable[..., Coroutine[Any, Any, None]]] = [
            SchedulerWorker.send_periodic_notifications,
            SchedulerWorker.send_scheduled_notifications,
        ]


class SchedulerWorker(BaseWorker):
    async def startup(self, ctx: WorkerContext) -> None:
        pass

    async def shutdown(self, ctx: WorkerContext) -> None:
        pass

    @staticmethod
    async def send_periodic_notifications(ctx: WorkerContext) -> None:
        current_time = datetime.now(UTC)
        async for session in get_session():
            state_service = NotificationStateService(session)
            notifications = await state_service.get_pending_periodic(current_time)
            for notification in notifications:
                message_body = {
                    "template_id": str(notification.template_id),
                    "context": notification.context,
                    "subscribers": [str(sub) for sub in notification.subscribers],
                    "event_type": notification.notification_type,
                    "notification_type": notification.notification_type,
                }
                queue = get_queue_for_event(EventType(notification.notification_type.value))
                priority = get_priority_for_event(EventType(notification.notification_type.value))
                await ctx["rabbitmq"].send_message(
                    queue_name=queue.queue_name,
                    message_body=orjson.dumps(message_body),
                    priority=priority,
                )
                await state_service.update_periodic_run_time(notification.id, current_time)

    @staticmethod
    async def send_scheduled_notifications(ctx: WorkerContext) -> None:
        current_time = datetime.now(UTC)
        async for session in get_session():
            state_service = NotificationStateService(session)
            notifications = await state_service.get_pending_scheduled(
                current_time,
                batch_size=settings.scheduled_batch_size,
            )
            for notification in notifications:
                message_body = {
                    "template_id": str(notification.template_id),
                    "context": notification.context,
                    "subscribers": [str(sub) for sub in notification.subscribers],
                    "event_type": notification.notification_type,
                    "notification_type": notification.notification_type,
                }
                queue = get_queue_for_event(EventType(notification.notification_type.value))
                priority = get_priority_for_event(EventType(notification.notification_type.value))
                await ctx["rabbitmq"].send_message(
                    queue_name=queue.queue_name,
                    message_body=orjson.dumps(message_body),
                    priority=priority,
                )
                await state_service.mark_scheduled_sent(notification.id)
