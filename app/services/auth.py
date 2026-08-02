from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.settings import settings
from core.jwt import create_access_token, create_refresh_token, decode_token
from database.models import RefreshTokenBase
from schemas.token import TokenResponse

def generate_tokens(
        user_id: int,
        db: Session
) -> TokenResponse:
    to_encode = {'sub': str(user_id)}

    access_expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
  
    access_token = create_access_token(
        data=to_encode,
        expire=access_expire
    )

    refresh_token = create_refresh_token(
        data=to_encode,
        expire=refresh_expire
    )

    refresh_token_db = RefreshTokenBase(
        user_id=user_id,
        token=refresh_token,
        expires_at=refresh_expire,
    )

    db.add(refresh_token_db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


def validate_refresh_token(
        token: str,
        db: Session,
) -> tuple[int, RefreshTokenBase]:
    
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'invalid token'
        )
    
    if payload.get('type') != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid token type'
        )

    refresh_token_db = (
        db.query(RefreshTokenBase)
        .filter(RefreshTokenBase.token == token)
        .first()
    )

    if refresh_token_db is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid refresh token"
        )

    if refresh_token_db.revoked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='token is inactive'
        )

    user_id = payload.get('sub')

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid token'
        )

    return user_id, refresh_token_db


def revoke_refresh_token(
        refresh_token_db: RefreshTokenBase
) -> None:

    refresh_token_db.revoked = True