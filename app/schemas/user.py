from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponce(BaseModel):
    id: int
    email: str
    name: str


class UserChangeName(BaseModel):
    new_name: str
    
    @field_validator('new_name')
    @classmethod
    def user_name_not_empty(cls, name: str) -> str:
        if not name.strip():
            raise ValueError('The name can not be empty')
        return name.strip()