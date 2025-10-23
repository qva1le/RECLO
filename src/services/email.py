# src/services/email.py
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid
import aiosmtplib

from src.config import settings
from src.services.base import BaseService


class EmailService(BaseService):
    async def _send_text(self, to_email: str, subject: str, body: str) -> None:
        msg = MIMEText(body, _subtype="plain", _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = formataddr(("Support", settings.SMTP_USER))  # <-- фикс
        msg["To"] = to_email
        msg["Message-ID"] = make_msgid(domain=settings.SMTP_HOST)

        # 587 — STARTTLS, 465 — SMTPS (SSL)
        use_ssl = (settings.SMTP_PORT == 465)

        if use_ssl:
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=True,
            )
        else:
            async with aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT) as smtp:
                await smtp.connect()
                await smtp.starttls()
                await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                await smtp.send_message(msg)

    async def verification_code(self, to_email: str, code: str) -> None:
        subject = "Код подтверждения"
        body = f"Ваш код — {code}\nОн действителен {settings.VERIFY_CODE_TTL_SECONDS//60} минут(ы)."
        await self._send_text(to_email, subject, body)
