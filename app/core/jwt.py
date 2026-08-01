from jose import jwt, JWTError
from datetime import datetime

from core.settings import settings


def create_access_token(data: dict, expire: datetime) -> str:
    to_encode = data.copy()
    to_encode['exp'] = expire
    to_encode['type'] = 'access'
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
    
