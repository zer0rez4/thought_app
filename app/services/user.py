from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from database.models import UserBase


def get_user_by_id(
        db: Session,
        user_id: int
) -> UserBase:
    
    user = (
        db.query(UserBase)
        .filter(UserBase.id == user_id)
        .first()
    )

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