# stdlib
from abc import ABC, abstractmethod


class SenderServiceBase(ABC):
    def __init__(self, message_body: str, target: str, subject: str) -> None:
        self.message_body = message_body
        self.target = target
        self.subject = subject

    @abstractmethod
    async def send_message(self) -> None:
        raise NotImplementedError


class SenderSendMessageError(Exception):
    pass
