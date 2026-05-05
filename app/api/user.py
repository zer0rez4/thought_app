from fastapi import APIRouter, Header, status, HTTPException, Depends, Response
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from schemas.user import UserChangeName, UserResponce
from database.database import get_db
from database.models import UserBase


router = APIRouter()


@router.get('/users/me', tags=['users'], response_model=UserResponce)
def get_user_me(
    user: UserBase = Depends(get_current_user)
    ):

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'user does not exist'
        )

    result = UserResponce(
        id = user.id,
        email = user.email,
        name = user.name
    )

    return result


# прописать
# @router.get('/users/{user_id}')
# def get_user(): pass


@router.patch('/users/me', tags=['users'], response_model=UserResponce)
def change_user_name(
    user_update: UserChangeName,
    user: UserBase = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):

    user.name = user_update.new_name

    db.commit()
    db.refresh(user)

    result = UserResponce(
        id = user.id,
        email = user.email,
        name = user.name
    )

    return result