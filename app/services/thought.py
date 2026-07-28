from fastapi import HTTPException, status
from sqlalchemy.orm import Session

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
        author_name: str
) -> ThoughtResponse:
    
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
        author_name = (
            user.name
            if thought.author_id == user.id
            else get_user_by_id(db, thought.author_id).name
        )
        
        thoughts.append(
            build_thought_response(
                thought=thought,
                author_name=author_name
            )
        )

    return ThoughtListResponse(
        items=thoughts,
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total
    )