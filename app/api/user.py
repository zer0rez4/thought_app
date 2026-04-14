from fastapi import APIRouter, Header, status, HTTPException, Depends, Response
from sqlalchemy.orm import Session

from schemas.user import UserChangeName, UserResponce
from database.database import get_db
from database.models import UserBase


router = APIRouter()

#прописать
@router.get('/users/{user_id}')
def get_user(): pass


@router.get('/users/me', response_model=UserResponce)
def get_user_me(
    user_id: int = Header(...),
    db: Session = Depends(get_db)
    ):

    user = db.query(UserBase).filter(UserBase.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'user does not exist'
        )

    result = UserResponce(
        id = user_id,
        email = user.email,
        name = user.name
    )

    return result


@router.patch('/users/me', response_model=UserResponce)
def change_user_name(
    user_update: UserChangeName,
    user_id: int = Header(...), 
    db: Session = Depends(get_db)
    ):

    user = db.query(UserBase).filter(UserBase.id == user_id).first()

    user.name = user_update.new_name

    db.commit()
    db.refresh(user)

    result = UserResponce(
        id = user_id,
        email = user.email,
        name = user.name
    )

    return result