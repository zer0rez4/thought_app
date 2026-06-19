from fastapi import APIRouter, Header, status, HTTPException, Depends, Response
from sqlalchemy import and_
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from schemas.user import UserUpdate, UserResponse, UserProfileResponse
from schemas.thoughts import ThoughtResponse
from database.database import get_db
from database.models import UserBase, ThoughtBase


router = APIRouter()


@router.get('/users/me', tags=['users'], response_model=UserResponse)
def get_user_me(
    user: UserBase = Depends(get_current_user)
    ):

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'user does not exist'
        )

    result = UserResponse(
        id = user.id,
        email = user.email,
        name = user.name,
        is_private = user.is_private
    )

    return result


@router.get('/users/{user_id}', tags=['users'], response_model=UserProfileResponse)
def get_user(
    user_id: int,
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db)
    ): 

    searched_user = db.query(UserBase).filter(UserBase.id == user_id).first()

    if not searched_user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'user is not exist'
        )

    if searched_user.is_private and searched_user.id != user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = 'account is private'
            )

    if searched_user.id == user.id:
        thoughts = db.query(ThoughtBase).filter(
            ThoughtBase.author_id == searched_user.id
            ).all()

    else:
        thoughts = db.query(ThoughtBase).filter(
            and_(
                ThoughtBase.author_id == searched_user.id,
                ThoughtBase.is_public.is_(True)
                )
            ).all()
    
    thought_list = [
        ThoughtResponse(
            id = thought.id,
            text = thought.text,
            author = searched_user.name,
            is_public = thought.is_public
        )
        for thought in thoughts
    ]

    return UserProfileResponse(
        name = searched_user.name,
        thoughts = thought_list
    )


@router.patch('/users/me', tags=['users'], response_model=UserResponse)
def user_update(
    user_update: UserUpdate,
    user: UserBase = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):

    if user_update.new_name is not None: 
        user.name = user_update.new_name
    if user_update.is_private is not None:
        user.is_private = user_update.is_private

    db.commit()
    db.refresh(user)

    result = UserResponse(
        id = user.id,
        email = user.email,
        name = user.name,
        is_private = user.is_private
    )

    return result