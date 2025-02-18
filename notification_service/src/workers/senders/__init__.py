# project
from enums.db import ChannelType

from .base import SenderSendMessageError, SenderServiceBase
from .email import EmailSenderService

SENDER_SERVICES: dict[ChannelType, type[SenderServiceBase] | None] = {
    ChannelType.EMAIL: EmailSenderService,
    ChannelType.SMS: None,
    ChannelType.PUSH: None,
}


__all__ = [
    "SENDER_SERVICES",
    "EmailSenderService",
    "SenderSendMessageError",
    "SenderServiceBase",
]
