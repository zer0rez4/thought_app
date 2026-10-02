import aiosmtplib

from email.message import EmailMessage

from app.core.settings import settings


async def send_email(
        recipient: str,
        subject: str,
        text_body: str,
        html_body: str
) -> None:
    message = EmailMessage()

    message["From"] = settings.SMTP_FROM
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(
        text_body, 
        charset="utf-8"
    )

    message.add_alternative(
        html_body,
        subtype='html'
    )

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD
    )