from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import UserBase
from app.core.security import verify_password


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
        user_email: str,
        password: str
) -> None:

    user = await get_user_by_email(
        db = db,
        user_email = user_email
    )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='account is already active'
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password is incorrect"
        )

    user.is_active = True
    await db.commit()


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