# stdlib
import logging
from collections.abc import AsyncGenerator
from uuid import UUID

# thirdparty
from jinja2 import Environment
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

# project
from enums.rabbitmq import MessageType
from repositories.sql.periodic_notification import (
    PeriodicNotificationRepository,
)
from repositories.sql.scheduled_notification import (
    ScheduledNotificationRepository,
)
from repositories.sql.template import TemplateRepository
from schemas.auth_service import UserData
from schemas.messages import RabbitMQMessage
from schemas.templates import TemplateResponse
from services.auth_service import auth_service
from services.url_shorter import URLShortener

logger = logging.getLogger(__name__)


class MessageProcessorService:
    def __init__(
        self,
        session: AsyncSession,
        message: RabbitMQMessage,
        redis: Redis,
        batch_processing: bool = False,
    ) -> None:
        self.session = session
        self.batch_processing = batch_processing
        self.redis = redis
        self.message = message
        self.template: TemplateResponse | None = None

    async def initialize(self) -> None:
        if not await self.check_message_status():
            raise MessageProcessorError("Message is not active")
        self.template = await self.get_template(self.message)

    async def process_message(self) -> AsyncGenerator[tuple[str, str, str], None]:
        self.template = await self.get_template(self.message)
        if self.batch_processing:
            return await self.batch_process_subscribers(self.message)

        return self.process_subscribers(self.message)

    async def check_message_status(self) -> bool:
        if self.message.message_type == MessageType.IMMEDIATE:
            return True
        match self.message.message_type:
            case MessageType.SCHEDULED:
                scheduled_repo = ScheduledNotificationRepository(self.session)
                return bool(await scheduled_repo.get(UUID(self.message.notification_id)))
            case MessageType.PERIODIC:
                periodic_repo = PeriodicNotificationRepository(self.session)
                return await periodic_repo.notification_is_active(UUID(self.message.notification_id))
            case _:
                logger.info(f'Unknown message type "{self.message.message_type}"')
                return False

    async def get_template(self, message: RabbitMQMessage) -> TemplateResponse:
        repo = TemplateRepository(self.session)
        db_template = await repo.get(UUID(message.template_id))
        if db_template is None:
            raise MessageProcessorError(f"Template {message.template_id} not found")
        return TemplateResponse.model_validate(db_template)

    async def process_subscribers(self, message: RabbitMQMessage) -> AsyncGenerator[tuple[str, str, str], None]:
        for subscriber in message.subscribers:
            if message.notification_id and await self.notification_sent(subscriber, message.notification_id):
                continue

            subscriber_data = await self.get_subscriber_data(subscriber)
            yield (
                subscriber,
                subscriber_data.email,
                await self.fill_template(subscriber_data.model_dump() | message.context),
            )

    async def notification_sent(self, subscriber: str, notification_id: str) -> bool:
        return await self.redis.exists(f"{subscriber}:{notification_id}")

    @staticmethod
    async def get_subscriber_data(subscriber_id: str) -> UserData:
        return await auth_service.get_user_data(subscriber_id)

    async def fill_template(self, subscriber_data: dict) -> str:
        if self.template is None:
            return ""

        url = subscriber_data.get("url")
        if url is not None:
            subscriber_data["url"] = URLShortener().shorten_url(url)

        env = Environment()
        template = env.from_string(self.template.body)
        return template.render(subscriber_data)

    async def batch_process_subscribers(self, message: RabbitMQMessage) -> AsyncGenerator:
        raise NotImplementedError


class MessageProcessorError(Exception):
    pass
