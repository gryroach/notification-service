# thirdparty
from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection, HeadersType
from aiormq import AMQPConnectionError

# project
from core.config import settings
from enums.rabbitmq import RabbitMQQueues
from schemas.messages import MessageResponse
from services.priorities import MAX_PRIORITY

EXCHANGE_NAME = "notifications"


class RabbitMQService:
    def __init__(self) -> None:
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None

    async def connect(self) -> None:
        self.connection = await self.get_connection()
        self.channel = await self.connection.channel()
        await self.channel.declare_exchange(EXCHANGE_NAME, ExchangeType.DIRECT)

    async def init_queues(self) -> None:
        await self.connect()
        assert self.channel is not None, "RabbitMQ channel is not initialized"

        for queue_conf in RabbitMQQueues.list_queues():
            queue = await self.channel.declare_queue(
                queue_conf.queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": queue_conf.ttl,
                    "x-max-priority": MAX_PRIORITY,
                },
            )
            await queue.bind(EXCHANGE_NAME, routing_key=queue_conf.queue_name)

    @staticmethod
    async def get_connection() -> AbstractRobustConnection:
        try:
            connection = await connect_robust(settings.rabbitmq_url)
        except AMQPConnectionError as err:
            raise ValueError("RabbitMQ connection error") from err
        return connection

    async def close(self) -> None:
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    async def send_message(
        self,
        queue_name: str,
        message_body: str | bytes,
        priority: int = 1,
        x_request_id: str | None = None,
    ) -> MessageResponse:
        """
        Отправляет сообщение в указанную очередь с заданным приоритетом и заголовком X-Request-Id.

        :param queue_name: Название очереди.
        :param message_body: Тело сообщения.
        :param priority: Приоритет сообщения (по умолчанию 1).
        :param x_request_id: Значение заголовка X-Request-Id (опционально).
        """
        if not self.channel:
            await self.connect()
            assert self.channel is not None, "RabbitMQ channel is not initialized"

        if isinstance(message_body, str):
            message_body = message_body.encode()

        headers: HeadersType = {}
        if x_request_id:
            headers["X-Request-Id"] = x_request_id

        message = Message(
            body=message_body,
            priority=priority,
            headers=headers,
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        try:
            await self.channel.default_exchange.publish(
                message,
                routing_key=queue_name,
            )
            return MessageResponse(
                status="success",
                message="Message successfully added to the queue",
                queue=queue_name,
                priority=priority,
                x_request_id=x_request_id,
            )
        except Exception as e:
            return MessageResponse(
                status="error",
                message=str(e),
                queue=queue_name,
                priority=priority,
                x_request_id=x_request_id,
            )
