from fastapi import APIRouter, status, HTTPException, Depends, Response, Query
from sqlalchemy import and_
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from core.security import verify_password
from schemas.user import UserUpdate, UserResponse, UserProfileResponse, UserRestore
from database.database import get_db
from database.models import UserBase, ThoughtBase
from services.user import get_user_by_id
from services.thought import (
    build_thought_list_response, 
    paginate_query,
    apply_search
)


router = APIRouter()


@router.get('/users/me', tags=['users', 'me'], response_model=UserResponse)
def get_user_me(
    user: UserBase = Depends(get_current_user)
    ):

    return UserResponse(
        id = user.id,
        email = user.email,
        name = user.name,
        is_private = user.is_private
    )


@router.patch('/users/me', tags=['users', 'me'], response_model=UserResponse)
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


@router.delete('/users/me', tags=['users', 'me'])
def delete_user(
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    user.is_active = False
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/users/restore', tags=['users'])
def restore_user(
    user_data: UserRestore,
    db: Session = Depends(get_db)
):
    
    user = db.query(UserBase).filter(UserBase.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'User does not exist'
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='account is already active'
        )

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password is incorrect"
        )

    user.is_active = True
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.get('/users/{user_id}', tags=['users'], response_model=UserProfileResponse)
def get_user(
    user_id: int,
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=20),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1)
    ): 

    searched_user = get_user_by_id(db=db, user_id=user_id)

    if searched_user.is_private and searched_user.id != user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = 'account is private'
            )

    if searched_user.id == user.id:
        query = db.query(ThoughtBase).filter(
            ThoughtBase.author_id == searched_user.id
            )

    else:
        query = db.query(ThoughtBase).filter(
            and_(
                ThoughtBase.author_id == searched_user.id,
                ThoughtBase.is_public.is_(True)
                )
            )
    
    query = apply_search(query, search)

    thoughts, total = paginate_query(
        query=query,
        limit=limit,
        offset=offset
    )

    thought_list = build_thought_list_response(
        thoughts_list=thoughts,
        user=searched_user,
        total=total,
        limit=limit,
        offset=offset
    )

    return UserProfileResponse(
        name = searched_user.name,
        thoughts = thought_list
    )
