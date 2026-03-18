from pydantic import BaseModel


class CreateThought(BaseModel):
    text: str
    author: str
    is_public: bool


class GetThought(BaseModel):
    id: int
    text: str
    author: str
    is_public: bool