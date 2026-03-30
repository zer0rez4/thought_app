from fastapi import APIRouter, Header, status, HTTPException
from typing import List

from schemas.thoughts import CreateThought, ThoughtResponse
from domain.thoughts import Thoughts

from api.auth import user_db_by_id

router = APIRouter()

thoughts_db = {}
thought_uniq_id = 1


@router.post('/thoughts/create')
def thought_create(
    thought: CreateThought,
    user_id: int = Header(...)
    ):

    global thought_uniq_id

    new_thought = Thoughts(
        thought_id = thought_uniq_id,
        text = thought.text,
        author_id = user_id,
        is_public = thought.is_public
    )

    thoughts_db[thought_uniq_id] = new_thought

    thought_uniq_id += 1

    author_name = user_db_by_id[user_id].user_name
    
    result = ThoughtResponse(
        id=new_thought.thought_id,
        text=new_thought.text,
        author=author_name,
        is_public=new_thought.is_public
    )
    
    return result


@router.get('/thoughts/{thought_id}')
def thought_get(
    thought_id: int,
    user_id: int = Header(...)
    ):
    
    if thought_id not in thoughts_db:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'thought does not exist'
        )
    
    db_data = thoughts_db[thought_id]
    author_name = user_db_by_id[db_data.author_id].user_name

    if not db_data.is_public:
        if db_data.author_id == user_id:
            return ThoughtResponse(id=db_data.thought_id, text=db_data.text, author=author_name, is_public=db_data.is_public)
        else:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = 'thought is not public'
            )
    else:
        return ThoughtResponse(id=db_data.thought_id, text=db_data.text, author=author_name, is_public=db_data.is_public)
    

### продербажить и замерджить

@router.get('/thoughts', response_model=List[ThoughtResponse])
def get_thoughts(
    user_id: int = Header(...)
    ):
    result = []

    for thought in thoughts_db.values():
        if thought.is_public or thought.author_id == user_id:
            author_name = user_db_by_id[thought.author_id].user_name

            result.append(
                ThoughtResponse(
                    id = thought.thought_id,
                    text = thought.text,
                    author = author_name,
                    is_public = thought.is_public
                )
            )

    return result