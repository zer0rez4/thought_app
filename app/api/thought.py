from fastapi import APIRouter

from schemas.thoughts import CreateThought, GetThought
from domain.thoughts import Thoughts


router = APIRouter()

thoughts_db = {}
thought_uniq_id = 1


@router.post('/thoughts/create')
def thought_create(thought: CreateThought):
    global thought_uniq_id

    
