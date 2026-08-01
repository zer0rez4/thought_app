from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from core.settings import settings
from core.jwt import create_access_token, create_refresh_token
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
