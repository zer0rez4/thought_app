from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserLogin, UserResponce
from core.security import hash_password, verify_password
from core.jwt import create_access_token
from database.database import get_db
from database.models import UserBase

router = APIRouter()


@router.post('/register')
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
    db.commit()
    db.refresh(new_user)

    to_encode = {'sub': str(new_user.id)}
    token = create_access_token(to_encode)

    return {
        'access_token': token,
        'token_type': "bearer"
    }



@router.post('/login')
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

    password_hash = log_user.hashed_password

    if verify_password(user.password, password_hash):
        to_encode = {'sub': str(log_user.id)}
        token = create_access_token(to_encode)

        return {
            'access_token': token,
            'token_type': 'bearer'
            }
    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'password is incorrect'
        )
