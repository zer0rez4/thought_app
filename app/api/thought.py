from fastapi import APIRouter, status, HTTPException, Response, Depends, Query
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.schemas.thoughts import CreateThought, ThoughtResponse, UpdateThought, ThoughtListResponse
from app.database.database import get_db
from app.database.models import ThoughtBase, UserBase
from app.core.dependencies import get_current_user
from app.services.user import get_user_by_id
from app.services.thought import (
    get_thought_by_id, 
    build_thought_response, 
    check_thought_read_access,
    check_thought_change_access,
    build_thought_list_response, 
    paginate_query, apply_search
)


router = APIRouter()


@router.post('/thoughts', tags=['thought'], response_model=ThoughtResponse)
def thought_create(
    thought: CreateThought,
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    new_thought = ThoughtBase(
        text = thought.text,
        author_id = user.id,
        is_public = thought.is_public
    )

    db.add(new_thought)
    db.commit()
    db.refresh(new_thought)

    return build_thought_response(
        thought = new_thought,
        author = user
    )


@router.get('/thoughts/random', tags=['thought'], response_model=ThoughtResponse)
def random_thought(db: Session = Depends(get_db)):
    thought = (
        db.query(ThoughtBase)
        .filter(ThoughtBase.is_public.is_(True))
        .order_by(func.random())
        .first()
    )

    if not thought:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'No available public thoughts'
        )

    user = get_user_by_id(db=db, user_id=thought.author_id)

    return build_thought_response(
        thought = thought,
        author = user
    )   


@router.get('/thoughts/my', tags=['thought'], response_model=ThoughtListResponse)
def my_thoughts(
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=20),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1)
    ):

    query = db.query(ThoughtBase).filter(
        ThoughtBase.author_id == user.id
    )

    query = apply_search(query, search)

    thoughts, total = paginate_query(
        query=query,
        limit=limit,
        offset=offset, 
    )

    return build_thought_list_response(
        thoughts_list=thoughts,
        user=user,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get('/thoughts/{thought_id}', tags=['thought'], response_model=ThoughtResponse)
def thought_get(
    thought_id: int,
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    
    thought = get_thought_by_id(db=db, thought_id=thought_id)
    
    author = get_user_by_id(db=db, user_id=thought.author_id)

    check_thought_read_access(thought=thought, user=user)

    return build_thought_response(
        thought = thought,
        author = author
    )


@router.get('/thoughts', tags=['thought'], response_model=ThoughtListResponse)
def get_thoughts(
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=20),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1)
    ):
    
    query = db.query(ThoughtBase).filter(
        or_(
            ThoughtBase.is_public.is_(True),
            ThoughtBase.author_id == user.id
        )
    )

    query = apply_search(query, search)

    thoughts, total = paginate_query(
        query=query,
        limit=limit,
        offset=offset
    )

    return build_thought_list_response(
        thoughts_list=thoughts,
        user=user,
        total=total,
        limit=limit,
        offset=offset,
        db=db
    )


@router.patch('/thoughts/{thought_id}', tags=['thought'], response_model = ThoughtResponse)
def change_thought(
    thought_id: int,
    thought_update: UpdateThought,
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    thought = get_thought_by_id(db=db, thought_id=thought_id)
    
    check_thought_change_access(thought=thought, user=user)

    if thought_update.text is not None:
        thought.text = thought_update.text

    if thought_update.is_public is not None:
        thought.is_public = thought_update.is_public
    
    db.commit()
    db.refresh(thought)

    return build_thought_response(
        thought = thought,
        author = user
    )


@router.delete('/thoughts/{thought_id}',  tags=['thought'])
def delete_thought(
    thought_id: int,
    user: UserBase = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    thought = get_thought_by_id(db=db, thought_id=thought_id)

    check_thought_change_access(thought=thought, user=user)
    
    db.delete(thought)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)