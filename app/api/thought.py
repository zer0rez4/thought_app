from fastapi import APIRouter, status, HTTPException, Response, Depends, Query
from sqlalchemy import or_, select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.thoughts import CreateThought, ThoughtResponse, UpdateThought, ThoughtListResponse
from app.database.database import get_db
from app.database.models import ThoughtBase, UserBase
from app.core.dependencies import get_current_user
from app.services.thought import (
    get_thought_by_id, 
    build_thought_response, 
    check_thought_read_access,
    check_thought_change_access,
    build_thought_list_response, 
    paginate_query, apply_search,
    create_thought, update_thought, delete_thought
)


router = APIRouter()


@router.post('/thoughts', tags=['thought'], response_model=ThoughtResponse)
async def thought_create(
    thought: CreateThought,
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):

    new_thought = await create_thought(
        db=db,
        author_id=user.id,
        text=thought.text,
        is_public=thought.is_public
    )

    return build_thought_response(
        thought = new_thought,
    )


@router.get('/thoughts/random', tags=['thought'], response_model=ThoughtResponse)
async def random_thought(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ThoughtBase)
        .options(selectinload(ThoughtBase.author))
        .where(ThoughtBase.is_public.is_(True))
        .order_by(func.random())
        .limit(1)
    )

    thought = result.scalar_one_or_none()

    if not thought:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'No available public thoughts'
        )

    return build_thought_response(
        thought = thought,
    )   


@router.get('/thoughts/my', tags=['thought'], response_model=ThoughtListResponse)
async def my_thoughts(
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=20),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1)
    ):

    query = (
        select(ThoughtBase)
        .options(selectinload(ThoughtBase.author))
        .where(ThoughtBase.author_id == user.id)
    )

    query = apply_search(query, search)

    thoughts, total = await paginate_query(
        db=db,
        query=query,
        limit=limit,
        offset=offset, 
    )

    return build_thought_list_response(
        thoughts_list=thoughts,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get('/thoughts/{thought_id}', tags=['thought'], response_model=ThoughtResponse)
async def thought_get(
    thought_id: int,
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    
    thought = await get_thought_by_id(db=db, thought_id=thought_id)
    
    check_thought_read_access(thought=thought, user=user)

    return build_thought_response(
        thought = thought,
    )


@router.get('/thoughts', tags=['thought'], response_model=ThoughtListResponse)
async def get_thoughts(
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=20),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1)
    ):

    query = (
        select(ThoughtBase)
        .options(selectinload(ThoughtBase.author))
        .where(
            or_(
                ThoughtBase.is_public.is_(True),
                ThoughtBase.author_id == user.id
            )
        )
    )

    query = apply_search(query, search)

    thoughts, total = await paginate_query(
        db=db,
        query=query,
        limit=limit,
        offset=offset
    )

    return build_thought_list_response(
        thoughts_list=thoughts,
        total=total,
        limit=limit,
        offset=offset
    )


@router.patch('/thoughts/{thought_id}', tags=['thought'], response_model = ThoughtResponse)
async def change_thought(
    thought_id: int,
    thought_update: UpdateThought,
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):

    thought = await get_thought_by_id(db=db, thought_id=thought_id)
    
    check_thought_change_access(thought=thought, user=user)

    updated_thought = await update_thought(
        db=db, 
        thought=thought, 
        text=thought_update.text, 
        is_public=thought_update.is_public
    )

    return build_thought_response(
        thought = updated_thought
    )


@router.delete('/thoughts/{thought_id}',  tags=['thought'])
async def thought_delete(
    thought_id: int,
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):

    thought = await get_thought_by_id(db=db, thought_id=thought_id)

    check_thought_change_access(thought=thought, user=user)

    await delete_thought(
        db=db,
        thought=thought
    )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)