from fastapi import APIRouter, HTTPException, status

from schemas.user import UserCreate, UserLogin, UserResponce
from domain.user import User
from core.security import hash_password, verify_password

router = APIRouter()


user_db_by_email = {}
user_db_by_id = {}
uniq_user_id = 1

@router.post('/register')
def register(user: UserCreate):
    global uniq_user_id

    if user.email in user_db_by_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'User already exists'
        )

    password_hash = hash_password(user.password)

    new_user = User(
        user_id = uniq_user_id,
        user_email = user.email,
        hashed_password = password_hash,  
        user_name = user.name
    )

    user_db_by_email[user.email] = new_user
    user_db_by_id[uniq_user_id] = new_user
    uniq_user_id += 1

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
