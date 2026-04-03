from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserLogin, UserResponce
from core.security import hash_password, verify_password
from database.database import get_db
from database.models import UserBase, ThoughtBase

router = APIRouter()


user_db_by_email = {}
user_db_by_id = {}
uniq_user_id = 1


@router.post('/register')
def register(user: UserCreate, db: Session=Depends(get_db)):
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

    return {'status': 'created'}



@router.post('/login')
def login(user: UserLogin):
    if user.email not in user_db_by_email:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'User does not exist'
        )

    db_data = user_db_by_email[user.email]
    password_hash = db_data.hashed_password

    if verify_password(user.password, password_hash):
        return UserResponce(id=db_data.user_id, email=user.email, name=db_data.user_name)
    else:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'password is incorrect'
        )
