from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.validators import validate_password

class EmailRequest(BaseModel):
    email: EmailStr

    @field_validator('email', mode='before')
    @classmethod
    def lower_email(cls, email: EmailStr) -> EmailStr:
        return email.strip().lower()


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

    _validate_password = field_validator('new_password')(
        validate_password
    )