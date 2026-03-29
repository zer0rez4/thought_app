from pydantic import BaseModel


class CreateThought(BaseModel):
    text: str
    is_public: bool


class ThoughtResponse(BaseModel):
    id: int
    text: str
    author: str
    is_public: bool