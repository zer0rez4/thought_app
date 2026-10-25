import aiosmtplib

from email.message import EmailMessage

from app.core.settings import settings
from app.utils.templates import render_email_template


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


async def send_action_email(
        recipient: str,
        user_name: str,
        token: str,
        *,
        url: str,
        template_prefix: str,
        link_name: str,
        subject: str
) -> None:

    action_link = (
        f"{url}?token={token}"
    )

    template_context = {
        link_name: action_link,
        "expire_time": settings.EMAIL_TOKEN_EXPIRE_MINUTES,
        "user_name": user_name
    }

    html = render_email_template(
        template_name=f'email/{template_prefix}_email.html',
        **template_context
    )

    text = render_email_template(
        template_name=f'email/{template_prefix}_email.txt',
        **template_context   
    )

    await send_email(
        recipient=recipient,
        subject=subject,
        text_body=text,
        html_body=html
    )

async def send_verification_email(
    recipient: str,
    user_name: str,
    token: str
) -> None:

    await send_action_email(
        recipient=recipient,
        user_name=user_name,
        token=token,
        url=settings.VERIFY_EMAIL_URL,
        template_prefix='verify',
        link_name='verification_link',
        subject='Подтверждение аккаунта Thoughts app'
    )


async def send_reset_password_email(
    recipient: str,
    user_name: str,
    token: str
) -> None:

    await send_action_email(
        recipient=recipient,
        user_name=user_name,
        token=token,
        url=settings.RESET_PASSWORD_URL,
        template_prefix='reset_password',
        link_name='reset_password_link',
        subject='Сброс пароля Thoughts app'
    )


async def send_restore_email(
    recipient: str,
    user_name: str,
    token: str
) -> None:

    await send_action_email(
        recipient=recipient,
        user_name=user_name,
        token=token,
        url=settings.RESTORE_ACCOUNT_URL,
        template_prefix='restore',
        link_name='restore_link',
        subject='Восстановление аккаунта Thoughts app'
    )
