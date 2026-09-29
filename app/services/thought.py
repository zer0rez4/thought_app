from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ThoughtBase, UserBase
from app.schemas.thoughts import ThoughtResponse, ThoughtListResponse


async def get_thought_by_id(
        db: AsyncSession,
        thought_id: int
) -> ThoughtBase:
    
    result = await db.execute(
        select(ThoughtBase)
        .options(selectinload(ThoughtBase.author))
        .where(ThoughtBase.id == thought_id)
    )

    thought = result.scalar_one_or_none()

    if not thought:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'thought does not exist'
        )
    
    return thought


def check_thought_read_access(
        thought: ThoughtBase,
        user: UserBase
) -> None:
    if not thought.is_public and thought.author_id != user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = 'user has no rights'
        )


def check_thought_change_access(
    thought: ThoughtBase,
    user: UserBase
) -> None:
    if thought.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user has no rights"
        )


def build_thought_response(
        thought: ThoughtBase
) -> ThoughtResponse:

    author_name = (
        thought.author.name
        if thought.author.is_active
        else "deleted user"
    )

    return ThoughtResponse(
        id = thought.id,
        text = thought.text,
        author = author_name,
        is_public = thought.is_public
    )


def build_thought_list_response(
        thoughts_list: list[ThoughtBase],
        total: int,
        limit: int,
        offset: int
) -> ThoughtListResponse:
    
    thoughts = []

    for thought in thoughts_list:       
        thoughts.append(
            build_thought_response(
                thought=thought
            )
        )

    return ThoughtListResponse(
        items=thoughts,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total
    )


async def paginate_query(
        db: AsyncSession,
        query,
        limit: int,
        offset: int,
) -> tuple[list[ThoughtBase], int]:

    items_result = await db.execute(
        query
        .offset(offset)
        .limit(limit)
    )

    items = items_result.scalars().all()

    total_result = await db.execute(
        select(func.count())
        .select_from(query.subquery())
    )

    total = total_result.scalar_one()

    return items, total


def apply_search(
        query,
        search: str | None = None
):
    
    if search:
        query = query.where(
            ThoughtBase.text.ilike(f'%{search}%')
        )

    return query


async def create_thought(
        db: AsyncSession,
        author_id: int,
        text: str,
        is_public: bool
) -> ThoughtBase:
    thought = ThoughtBase(
        text = text,
        author_id = author_id,
        is_public = is_public
    )

    db.add(thought)
    await db.commit()
    await db.refresh(thought, attribute_names=["author"])

    return thought


async def update_thought(
    db: AsyncSession,
    thought: ThoughtBase,
    text: str | None = None,
    is_public: bool | None = None
) -> ThoughtBase:
    if text is not None:
        thought.text = text

    if is_public is not None:
        thought.is_public = is_public

    await db.commit()
    await db.refresh(thought)

    return thought


async def delete_thought(
    db: AsyncSession,
    thought: ThoughtBase
) -> None:
    await db.delete(thought)
    await db.commit()