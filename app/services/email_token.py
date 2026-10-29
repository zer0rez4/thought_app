from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from app.core.email import (generate_email_token)
from app.core.security import hash_token
from app.core.settings import settings
from app.database.models import EmailTokenBase


async def create_email_token(
        db: AsyncSession, 
        user_id: int, 
        purpose: str
) -> str:

    token = generate_email_token()
    hashed_token = hash_token(token)

    created = datetime.now(timezone.utc)
    expire = created + timedelta(
        minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES
    )

    new_token = EmailTokenBase(
        user_id = user_id,
        token_hash = hashed_token,
        purpose = purpose,
        expires_at = expire,
        used_at = None,
        created_at = created
    )

    db.add(new_token)
    
    return token


async def validate_email_token(
        db: AsyncSession, 
        token: str,
        purpose: str
) -> EmailTokenBase:

    hashed_token = hash_token(token)

    result = await db.execute(
        select(EmailTokenBase)
        .where(EmailTokenBase.token_hash == hashed_token)
    )

    token_from_db = result.scalar_one_or_none()

    if token_from_db is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Invalid token'
        )

    current_time = datetime.now(timezone.utc)

    if current_time >= token_from_db.expires_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Token has expired'
        )

    if token_from_db.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Token has already been used'
        )

    if token_from_db.purpose != purpose:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid token purpose'
        )

    return token_from_db


def invalidate_token(
        token: EmailTokenBase
) -> None:

    token.used_at = datetime.now(timezone.utc)


async def check_resend_cooldown(
        db: AsyncSession,
        user_id: int,
        purpose: str,
        time_delta: int
) -> None:

    result = await db.execute(
        select(EmailTokenBase)
        .where(
            EmailTokenBase.user_id == user_id,
            EmailTokenBase.purpose == purpose
        )
        .order_by(EmailTokenBase.created_at.desc())
        .limit(1)
    )

    last_token = result.scalar_one_or_none()

    if last_token is None:
        return

    current_time = datetime.now(timezone.utc)
    cooldown = timedelta(seconds=time_delta)

    if current_time < last_token.created_at + cooldown:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='Please wait before requesting another email'
        )


async def delete_user_tokens_by_purpose(
        db: AsyncSession,
        user_id: int,
        purpose: str
) -> None:

    stmt = (
        delete(EmailTokenBase)
        .where(
            and_(
                EmailTokenBase.user_id == user_id,
                EmailTokenBase.purpose == purpose
            )
        )
    )

    await db.execute(stmt)
