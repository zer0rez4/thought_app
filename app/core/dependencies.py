from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import UserBase
from app.core.jwt import decode_token
from app.services.user import check_user_active, get_user_by_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserBase:

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'invalid token'
        )
    
    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid token type'
        )

    user_id = int(payload.get('sub'))

    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'invalid token payload'
        )

    user_data = get_user_by_id(db=db, user_id=user_id)

    check_user_active(user=user_data)

    return user_data
