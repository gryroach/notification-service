# stdlib
import logging
from email.message import EmailMessage

# thirdparty
import aiosmtplib
import backoff

# project
from core.config import settings
from workers.senders import SenderSendMessageError, SenderServiceBase

logger = logging.getLogger(__name__)


class EmailSenderService(SenderServiceBase):
    async def send_message(self) -> None:
        try:
            await self._send_message()
        except aiosmtplib.SMTPException as e:
            logger.error(f"Failed to send email to {self.target} after multiple attempts: {e}")
            raise SenderSendMessageError(f"Failed to send email to {self.target} after multiple attempts")

    @backoff.on_exception(backoff.expo, aiosmtplib.SMTPException, max_tries=5)
    async def _send_message(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = self.subject
        msg["From"] = settings.email_from
        msg["To"] = self.target

        msg.set_content(self.message_body, subtype="html")

        async with aiosmtplib.SMTP(hostname=settings.smtp_server, port=settings.smtp_port) as smtp:
            await smtp.login(settings.smtp_user, settings.smtp_password)
            await smtp.send_message(msg)
            logger.info(f"Email successfully sent to {self.target}")
