# stdlib
import asyncio
import logging
import sys

# thirdparty
from redis.asyncio import Redis

# project
from core.config import settings
from db.db import async_session
from enums.rabbitmq import RabbitMQQueues
from schemas.messages import RabbitMQMessage
from services.rabbitmq import RabbitMQService
from workers.former.message_processor import (
    MessageProcessorError,
    MessageProcessorService,
)
from workers.senders import SENDER_SERVICES
from workers.senders.base import SenderSendMessageError

logger = logging.getLogger(__name__)
EXPECTED_ARG_COUNT = 2


class FormerWorker:
    def __init__(self, queue_name: str) -> None:
        self.queue_name = queue_name
        self.redis = Redis.from_url(settings.redis_url)

    async def consume_messages(self) -> None:
        service = RabbitMQService()
        await service.init_queues()

        assert service.channel is not None, "RabbitMQ channel is not initialized"

        queue = await service.channel.get_queue(self.queue_name)
        if queue is None:
            raise ValueError(f"Queue {self.queue_name} does not exist")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    async with async_session() as session:
                        rabbit_message = RabbitMQMessage.model_validate_json(message.body.decode())
                        processor = MessageProcessorService(session, rabbit_message, self.redis)
                        try:
                            await processor.initialize()
                        except MessageProcessorError as e:
                            logger.warning(f"Failed to process message: {e}")
                            continue
                        await self.send_notification(rabbit_message, processor, message.body.decode())

    async def send_notification(
        self, rabbit_message: RabbitMQMessage, processor: MessageProcessorService, origin_message: str
    ) -> None:
        async for subscriber, subscriber_email, formed_message in await processor.process_message():
            sender_service_class = SENDER_SERVICES.get(rabbit_message.channel_type)
            if sender_service_class is None:
                logger.error(f"Sender service for channel type {rabbit_message.channel_type} not found")
                continue
            sender_service = sender_service_class(
                target=subscriber_email,
                subject=rabbit_message.context.get("subject", settings.default_notification_subject),
                message_body=formed_message,
            )
            try:
                await sender_service.send_message()
            except SenderSendMessageError:
                logger.warning(f"Failed to send message to {subscriber_email}")
                await self.redis.rpush(self.queue_name, origin_message)
            else:
                if rabbit_message.notification_id is not None:
                    await self.redis.setex(
                        f"{subscriber}:{rabbit_message.notification_id}", settings.redis_message_ttl, 1
                    )


if __name__ == "__main__":
    if len(sys.argv) != EXPECTED_ARG_COUNT:
        logger.error("Usage: python former_worker.py <queue_name>")
        sys.exit(1)

    worker_queue = sys.argv[1]
    if worker_queue not in RabbitMQQueues.list_names():
        logger.error(f"Queue {worker_queue} does not exist")
        sys.exit(1)

    former_worker = FormerWorker(worker_queue)

    asyncio.run(former_worker.consume_messages())
