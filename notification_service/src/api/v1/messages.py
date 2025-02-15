# stdlib
from typing import Annotated

# thirdparty
import orjson
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

# project
from db.db import get_session
from enums.db import get_priority_for_event
from enums.rabbitmq import get_queue_for_event
from repositories.sql.template import TemplateRepository
from schemas.messages import Message, MessageResponse
from services.rabbitmq import RabbitMQService

router = APIRouter()


@router.post(
    "/send-message/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    description="Отправление сообщения в очередь на отправку",
    summary="Отправление сообщения в очередь",
)
async def send_message(
    message: Message,
    rabbitmq_service: Annotated[RabbitMQService, Depends(RabbitMQService)],
    db: Annotated[AsyncSession, Depends(get_session)],
    request: Request,
) -> MessageResponse:
    template_repo = TemplateRepository(db)
    template = await template_repo.get(message.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    message_body = orjson.dumps(
        {
            "context": message.context,
            "subscribers": [str(m) for m in message.subscribers],
            "template_id": str(template.id),
            "event_type": message.event_type,
            "channel_type": message.channel_type,
            "notification_id": None,
        },
    )
    queue = get_queue_for_event(message.event_type)
    priority = get_priority_for_event(message.event_type)

    result = await rabbitmq_service.send_message(
        queue_name=queue.queue_name,
        message_body=message_body,
        priority=priority,
        x_request_id=request.headers.get("X-Request-Id"),
    )
    return result
