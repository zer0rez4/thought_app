from pydantic import BaseModel, EmailStr, field_validator, Field
from schemas.thoughts import ThoughtResponse


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str

    @field_validator('password')
    @classmethod
    def check_password(cls, password: str) -> str:
        if not password.strip():
            raise ValueError('The password can not be empty')
        return password

    @field_validator('name')
    @classmethod
    def user_name_not_empty(cls, name: str) -> str:
        if not name.strip():
            raise ValueError('The name can not be empty')
        return name.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_private: bool


class UserProfileResponse(BaseModel):
    name: str
    thoughts: list[ThoughtResponse]


class UserUpdate(BaseModel):
    new_name: str | None = None
    is_private: bool | None = None
    
    @field_validator('new_name')
    @classmethod
    def user_name_not_empty(cls, name: str) -> str:
        if name is None:
            return name
        
        if not name.strip():
            raise ValueError('The name can not be empty')
        return name.strip()