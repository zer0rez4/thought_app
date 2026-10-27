from fastapi import APIRouter, status, HTTPException, Depends, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.settings import settings
from app.schemas.user import (
    UserUpdate, UserResponse, 
    UserProfileResponse
)
from app.schemas.response import MessageResponse
from app.schemas.email import EmailRequest
from app.database.database import get_db
from app.database.models import UserBase, ThoughtBase
from app.services.user import (
    get_user_by_id, restore_user,
    get_user_by_email
)
from app.services.thought import (
    build_thought_list_response, 
    paginate_query,
    apply_search
)
from app.services.email_token import (
    create_email_token, delete_user_tokens_by_purpose,
    validate_email_token, invalidate_token,
    check_resend_cooldown
)
from app.services.email import send_restore_email


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
async def user_update(
    user_update: UserUpdate,
    user: UserBase = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
    ):

    if user_update.new_name is not None: 
        user.name = user_update.new_name
    if user_update.is_private is not None:
        user.is_private = user_update.is_private

    await db.commit()
    await db.refresh(user)

    result = UserResponse(
        id = user.id,
        email = user.email,
        name = user.name,
        is_private = user.is_private
    )

    return result


@router.delete(
        '/users/me', 
        tags=['users', 'me'],
        status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    user.is_active = False
    await db.commit()


@router.post(
        '/users/restore', 
        tags=['users', 'restore'],
        response_model=MessageResponse,
        status_code=status.HTTP_200_OK
)
async def request_account_restore(
    data: EmailRequest,
    db: AsyncSession = Depends(get_db)
):

    user = await get_user_by_email(
        db=db,
        user_email=data.email
    )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='account is already active'
        )

    await check_resend_cooldown(
        db=db,
        user_id=user.id,
        purpose='account_restore',
        time_delta=settings.RESEND_RESTORE_ACCOUNT_COOLDOWN_SECONDS
    )

    await delete_user_tokens_by_purpose(
        db=db,
        user_id=user.id,
        purpose='account_restore'
    )

    token = await create_email_token(
        db=db,
        user_id=user.id,
        purpose='account_restore'
    )

    await db.commit()

    await send_restore_email(
        recipient=user.email,
        user_name=user.name,
        token=token
    )

    return MessageResponse(
        detail='Restore email sent. Check your email.'
    )


@router.get(
        '/users/restore',
        tags=['users', 'restore'],
        response_model=MessageResponse,
        status_code=status.HTTP_200_OK
)
async def confirm_restore_user(
    token: str,
    db: AsyncSession = Depends(get_db)
):

    token_from_db = await validate_email_token(
        db=db,
        token=token,
        purpose='account_restore'
    )

    invalidate_token(token=token_from_db)

    await restore_user(
        db=db,
        user_id=token_from_db.user_id
    )

    await db.commit()

    return MessageResponse(
        detail='Account is restored'
    )


@router.get('/users/{user_id}', tags=['users'], response_model=UserProfileResponse)
async def get_user(
    user_id: int,
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=20),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1)
    ): 

    searched_user = await get_user_by_id(db=db, user_id=user_id)

    if searched_user.is_private and searched_user.id != user.id:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = 'account is private'
            )

    query = (
        select(ThoughtBase)
        .options(selectinload(ThoughtBase.author))
    )

    if searched_user.id == user.id:
        query = query.where(
            ThoughtBase.author_id == searched_user.id
        )

    else:
        query = query.where(
            and_(
                ThoughtBase.author_id == searched_user.id,
                ThoughtBase.is_public.is_(True)
            )
        )
    
    query = apply_search(query, search)

    thoughts, total = await paginate_query(
        db=db,
        query=query,
        limit=limit,
        offset=offset
    )

    thought_list = build_thought_list_response(
        thoughts_list=thoughts,
        total=total,
        limit=limit,
        offset=offset
    )

    return UserProfileResponse(
        name = searched_user.name,
        thoughts = thought_list
    )
