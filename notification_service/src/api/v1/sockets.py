# stdlib
from typing import Annotated

# thirdparty
from fastapi import APIRouter, Cookie, Depends, WebSocket
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse
from starlette.websockets import WebSocketDisconnect

# project
from core.config import STATIC_DIR
from db.db import get_session
from enums.db import get_priority_for_event
from enums.rabbitmq import MessageType, get_queue_for_event
from exceptions.auth_exceptions import AuthError
from repositories.sql.template import TemplateRepository
from schemas.messages import Message, RabbitMQMessage
from services.jwt_token import JWTBearer
from services.rabbitmq import RabbitMQService

router = APIRouter()


@router.get(
    "/",
    response_class=FileResponse,
    description="Веб-сокет для непрерывной отправки сообщений",
    summary="Веб-сокет отправки сообщений",
)
async def get() -> FileResponse:
    return FileResponse(STATIC_DIR / "message_client.html")


@router.websocket("/ws/send-message")
async def websocket_endpoint(
    websocket: WebSocket,
    rabbitmq_service: Annotated[RabbitMQService, Depends(RabbitMQService)],
    db: Annotated[AsyncSession, Depends(get_session)],
    access_token: Annotated[str, Cookie(description="JWT-токен доступа")] = "",
) -> None:
    await websocket.accept()
    try:
        JWTBearer().verify_jwt(access_token)
    except AuthError:
        await websocket.send_json({"status": "auth_error", "detail": "Ошибка авторизации, проверьте куки"})
        return

    try:
        while True:
            data = await websocket.receive_json()
            try:
                message = Message(**data)
            except ValidationError as e:
                await websocket.send_json({"status": "validation_error", "detail": str(e)})
                continue

            template_repo = TemplateRepository(db)
            template = await template_repo.get(message.template_id)
            if not template:
                await websocket.send_json({"status": "validation_error", "detail": "Шаблон не найден!"})
                continue

            message_body = RabbitMQMessage(
                context=message.context,
                subscribers=[str(m) for m in message.subscribers],
                template_id=str(template.id),
                event_type=message.event_type,
                channel_type=message.channel_type,
                notification_id=None,
                message_type=MessageType.IMMEDIATE,
            )

            queue = get_queue_for_event(message.event_type)
            priority = get_priority_for_event(message.event_type)

            result = await rabbitmq_service.send_message(
                queue_name=queue.queue_name,
                message_body=message_body.model_dump_json(),
                priority=priority,
                x_request_id=None,
            )
            await websocket.send_json({"status": result.status, "result": result.message})
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as e:
        await websocket.send_json({"status": "error", "detail": str(e)})
        await websocket.close()
