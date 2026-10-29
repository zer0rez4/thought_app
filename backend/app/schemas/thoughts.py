from pydantic import BaseModel, field_validator
from typing import Optional


class CreateThought(BaseModel):
    text: str
    is_public: bool

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, text: str) -> str:
        if not text.strip():
            raise ValueError('Text can not be empty')
        return text.strip()

class UpdateThought(BaseModel):
    text: Optional[str] = None
    is_public: Optional[bool] = None

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, text: Optional[str]) -> Optional[str]:
        if text is None:
            return None

        text = text.strip()

        if not text:
            raise ValueError('Text can not be empty')
        return text

class ThoughtResponse(BaseModel):
    id: int
    text: str
    author: str
    is_public: bool


class ThoughtListResponse(BaseModel):
    items: list[ThoughtResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
