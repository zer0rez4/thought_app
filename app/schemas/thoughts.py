from pydantic import BaseModel
from typing import Optional


class CreateThought(BaseModel):
    text: str
    is_public: bool


class UpdateThought(BaseModel):
    text: Optional[str] = None
    is_public: Optional[bool] = None


class ThoughtResponse(BaseModel):
    id: int
    text: str
    author: str
    is_public: bool