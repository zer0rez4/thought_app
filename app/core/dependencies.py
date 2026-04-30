from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import UserBase
from core.jwt import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    ):

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'invalid token'
        )
    
    user_id = payload.get('sub')

    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'invalid token payload'
        )

    user_data = db.query(UserBase).filter(UserBase.id == int(user_id)).first()

    if user_data is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'user not found'
        )

    return user_data

    