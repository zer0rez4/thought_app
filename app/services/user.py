from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserBase


async def get_user_by_id(
        db: AsyncSession,
        user_id: int
) -> UserBase:

    result = await db.execute(
        select(UserBase)
        .where(UserBase.id == user_id)
    )

    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'user not found'
        )
    
    return user


async def get_user_by_email(
        db: AsyncSession,
        user_email: str
) -> UserBase:

    result = await db.execute(
        select(UserBase)
        .where(UserBase.email == user_email)
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'User does not exist'
        )

    return user


async def restore_user(
        db: AsyncSession,
        user_id: int
) -> None:

    user = await get_user_by_id(
        db = db,
        user_id = user_id
    )

    user.is_active = True


def check_user_active(
        user: UserBase
) -> None:

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='account is deleted'
        )


def check_user_verified_email(
        user: UserBase
) -> None:

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='email is not verified'
        )