from fastapi import HTTPException, status
from sqlalchemy.orm import Session, Query

from database.models import ThoughtBase, UserBase
from schemas.thoughts import ThoughtResponse, ThoughtListResponse
from services.user import get_user_by_id


def get_thought_by_id(
        db: Session,
        thought_id: int
) -> ThoughtBase:
    
    thought = (
        db.query(ThoughtBase)
        .filter(ThoughtBase.id == thought_id)
        .first()
    )

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


def build_thought_response(
        thought: ThoughtBase, 
        author: UserBase
) -> ThoughtResponse:

    author_name = (
        author.name
        if author.is_active
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
        user: UserBase,
        total: int,
        limit: int,
        offset: int,
        db: Session | None = None
) -> ThoughtListResponse:
    
    thoughts = []

    for thought in thoughts_list:
        author = (
            user
            if thought.author_id == user.id
            else get_user_by_id(db, thought.author_id)
        )
        
        thoughts.append(
            build_thought_response(
                thought=thought,
                author=author
            )
        )

    return ThoughtListResponse(
        items=thoughts,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total
    )


def paginate_query(
        query: Query,
        limit: int,
        offset: int,
) -> tuple[list[ThoughtBase], int]:

    items = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    total = query.count()

    return items, total


def apply_search(
        query: Query,
        search: str | None = None
) -> Query:
    
    if search:
        query = query.filter(
            ThoughtBase.text.ilike(f'%{search}%')
        ) 

    return query