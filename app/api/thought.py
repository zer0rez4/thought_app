from fastapi import APIRouter, Header, status, HTTPException, Response, Depends
from typing import List
from random import choice
from sqlalchemy import or_
from sqlalchemy.orm import Session

from schemas.thoughts import CreateThought, ThoughtResponse, UpdateThought
from database.database import get_db
from database.models import ThoughtBase, UserBase

router = APIRouter()

@router.post('/thoughts', response_model=ThoughtResponse)
def thought_create(
    thought: CreateThought,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
    ):

    new_thought = ThoughtBase(
        text = thought.text,
        author_id = user_id,
        is_public = thought.is_public
    )

    try:
        db.add(new_thought)
        db.commit()
        db.refresh(new_thought)
    except Exception:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Field "text" must not be empty'
        )

    author_name = db.query(UserBase).filter(UserBase.id == user_id).first().name

    result = ThoughtResponse(
        id=new_thought.id,
        text=new_thought.text,
        author=author_name,
        is_public=new_thought.is_public
    )
    
    return result


@router.get('/thoughts/random', response_model=ThoughtResponse)
def random_thought(db: Session = Depends(get_db)):
    public_thoughts = db.query(ThoughtBase).filter(ThoughtBase.is_public == True).all()

    if not public_thoughts:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'No public thoughts'
        )

    thought = choice(public_thoughts)

    author_name = db.query(UserBase).filter(UserBase.id == thought.author_id).first().name

    return ThoughtResponse(
        id = thought.id,
        text = thought.text,
        author = author_name,
        is_public = thought.is_public
    )


@router.get('/thoughts/my', response_model=List[ThoughtResponse])
def my_thoughts(
    user_id: int = Header(...),
    db: Session = Depends(get_db)
    ):

    thoughts = db.query(ThoughtBase).filter(ThoughtBase.author_id == user_id).all()
    author_name = db.query(UserBase).filter(UserBase.id == user_id).first().name

    result = []

    for thought in thoughts:

        result.append(
            ThoughtResponse(
                id = thought.id,
                text = thought.text,
                author = author_name,
                is_public = thought.is_public
            )
        )
 
    return result
    

@router.get('/thoughts/{thought_id}', response_model=ThoughtResponse)
def thought_get(
    thought_id: int,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
    ):
    
    thought = db.query(ThoughtBase).filter(ThoughtBase.id == thought_id).first()
    
    if not thought:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'thought does not exist'
        )
    
    author_name = db.query(UserBase).filter(UserBase.id == thought.author_id).first().name

    if not thought.is_public:
        if thought.author_id == user_id:
            return ThoughtResponse(
                id=thought.id,
                text=thought.text,
                author=author_name,
                is_public=thought.is_public
                )
        else:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = 'thought is not public'
            )
    else:
        return ThoughtResponse(
            id=thought.id,
            text=thought.text,
            author=author_name,
            is_public=thought.is_public
            )


@router.get('/thoughts', response_model=List[ThoughtResponse])
def get_thoughts(
    user_id: int = Header(...),
    db: Session = Depends(get_db)
    ):
    result = []

    thoughts = db.query(ThoughtBase).filter(
        or_(
            ThoughtBase.is_public == True,
            ThoughtBase.author_id == user_id
            )
        ).all()

    for thought in thoughts:
        author_name = db.query(UserBase).filter(UserBase.id == thought.author_id).first().name

        result.append(
            ThoughtResponse(
                id = thought.id,
                text = thought.text,
                author = author_name,
                is_public = thought.is_public
            )
        )

    return result

@router.patch('/thoughts/{thought_id}', response_model = ThoughtResponse)
def change_thought(
    thought_id: int,
    thought_update: UpdateThought,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
    ):

    thought = db.query(ThoughtBase).filter(ThoughtBase.id == thought_id).first()

    if not thought:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'thought does not exist'
        )
    
    if thought.author_id != user_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = 'user has no rights'
        )
    
    if thought_update.text is not None:
        thought.text = thought_update.text

    if thought_update.is_public is not None:
        thought.is_public = thought_update.is_public
    
    db.commit()
    db.refresh(thought)

    author = db.query(UserBase).filter(UserBase.id == user_id).first().name

    return ThoughtResponse(
        id = thought.id,
        text = thought.text,
        author = author,
        is_public = thought.is_public
    )


@router.delete('/thoughts/{thought_id}')
def delete_thought(
    thought_id: int,
    user_id: int = Header(...),
    db: Session = Depends(get_db)
    ):

    thought = db.query(ThoughtBase).filter(ThoughtBase.id == thought_id).first()

    if not thought:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'thought does not exist'
        )

    if thought.author_id != user_id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = 'user has no rights'
        )

    db.delete(thought)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)