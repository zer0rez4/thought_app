from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserLogin
from schemas.token import TokenResponse, RefreshTokenRequest
from core.security import hash_password, verify_password
from database.database import get_db
from database.models import UserBase
from services.user import check_user_active
from services.auth import (
    generate_tokens, 
    validate_refresh_token,
    revoke_refresh_token)

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

    user_id, refresh_token_db = validate_refresh_token(
        token=token.refresh_token,
        db=db
    )

    tokens = generate_tokens(
        user_id=user_id,
        db=db
    )

    revoke_refresh_token(refresh_token_db=refresh_token_db)

    db.commit()

    return tokens


@router.post('/logout', tags=['auth'])
def logout(
    token: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    
    _, refresh_token_db = validate_refresh_token(
        token=token.refresh_token,
        db=db
    )

    revoke_refresh_token(refresh_token_db=refresh_token_db)

    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    ) 

