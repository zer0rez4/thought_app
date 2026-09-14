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


def check_user_active(
        user: UserBase
) -> None:

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='account is deleted'
        )