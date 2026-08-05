from jose import jwt, JWTError
from datetime import datetime
from uuid import uuid4

from app.core.settings import settings


def create_access_token(data: dict, expire: datetime) -> str:
    to_encode = data.copy()
    to_encode['exp'] = expire
    to_encode['type'] = 'access'
    to_encode['jti'] = str(uuid4())
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict, expire: datetime) -> str:
    to_encode = data.copy()
    to_encode['exp'] = expire
    to_encode['type'] = 'refresh'
    to_encode['jti'] = str(uuid4())
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    
    except JWTError:
        return None
    
