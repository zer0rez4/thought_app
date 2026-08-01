from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserLogin
from schemas.token import TokenResponse, RefreshTokenRequest
from core.security import hash_password, verify_password
from core.jwt import decode_token
from database.database import get_db
from database.models import UserBase, RefreshTokenBase
from services.user import check_user_active
from services.auth import generate_tokens

router = APIRouter()


@router.post('/register', tags=['auth'], response_model=TokenResponse)
def register(
    user: UserCreate, 
    db: Session=Depends(get_db)
    ):

    existing_user = db.query(UserBase).filter(UserBase.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'User already exists'
        )

    password_hash = hash_password(user.password)

    new_user = UserBase(
        email = user.email,
        hashed_password = password_hash,  
        name = user.name

    )

    db.add(new_user)
    db.flush()

    token_response = generate_tokens(
        user_id=new_user.id,
        db=db
    )

    db.commit()

    return token_response



@router.post('/login', tags=['auth'], response_model=TokenResponse)
def login(
    user: UserLogin,
    db: Session=Depends(get_db)
    ):

    log_user = db.query(UserBase).filter(UserBase.email == user.email).first()
    
    if not log_user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'User does not exist'
        )

    check_user_active(user=log_user)

    if verify_password(user.password, log_user.hashed_password):
        token_response = generate_tokens(
            user_id=log_user.id,
            db=db
        )

        db.commit()

        return token_response
    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'password is incorrect'
        )


@router.post('/refresh')
def refresh(
    token: RefreshTokenRequest,
    db: Session=Depends(get_db)
):

    payload = decode_token(token.refresh_token)

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
        .filter(RefreshTokenBase.token == token.refresh_token)
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

    tokens = generate_tokens(
        user_id=user_id,
        db=db
    )

    refresh_token_db.revoked = True

    db.commit()
    db.refresh(refresh_token_db)

    return tokens


@router.post('/logout', tags=['auth'])
def logout(
    db: Session = Depends(get_db)
):
    
    pass

