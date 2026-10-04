from fastapi import APIRouter, HTTPException, status, Depends, Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import TokenResponse, RefreshTokenRequest
from app.schemas.response import MessageResponse
from app.schemas.email import EmailRequest
from app.core.security import hash_password, verify_password
from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.database.models import UserBase, RefreshTokenBase
from app.services.user import (
    check_user_active, check_user_verified_email,
    get_user_by_email
)
from app.services.auth import (
    generate_tokens, 
    validate_refresh_token,
    revoke_refresh_token
)
from app.services.email_token import (
    create_email_token, validate_email_token,
    invalidate_token, delete_user_verification_tokens,
    check_resend_cooldown
)
from app.services.email import send_verification_email


router = APIRouter(
    prefix='/auth'
)


@router.post(
        '/register', 
        tags=['auth'], 
        response_model=MessageResponse,
        status_code=status.HTTP_201_CREATED
)
async def register(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
    ):

    result = await db.execute(
        select(UserBase).where(
            UserBase.email == user.email
        )
    )

    existing_user = result.scalar_one_or_none()

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
    await db.flush()

    token = await create_email_token(
        db = db,
        user_id = new_user.id,
        purpose='email_verification'
    )

    await db.commit()

    await send_verification_email(
        recipient=new_user.email,
        token=token
    )

    return MessageResponse(
        detail="Registration successful. Check your email."
    )


@router.post(
        '/resend-verification', 
        tags=['auth'], 
        response_model=MessageResponse,
        status_code=status.HTTP_200_OK
)
async def resend_verification(
    email: EmailRequest,
    db: AsyncSession = Depends(get_db)
):

    user = await get_user_by_email(
        db=db,
        user_email=email.email
    )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='email is already verified'
        )

    await check_resend_cooldown(
        db=db,
        user_id=user.id,
        purpose='email_verification'
    )

    await delete_user_verification_tokens(
        db=db,
        user_id=user.id,
        purpose='email_verification'
    )

    token = await create_email_token(
        db = db,
        user_id = user.id,
        purpose='email_verification'
    )

    await db.commit()

    await send_verification_email(
        recipient=user.email,
        token=token
    )

    
    return MessageResponse(
            detail="Verification email sent. Check your email."
        )



@router.get(
        '/verify-email',
        tags=['auth'], 
        response_model=MessageResponse,
        status_code=status.HTTP_200_OK
)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):

    token_from_db = await validate_email_token(
        db = db,
        token = token,
        purpose = 'email_verification'
    )

    invalidate_token(token=token_from_db,)

    result = await db.execute(
        select(UserBase)
        .where(UserBase.id == token_from_db.user_id)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    user.email_verified = True

    await db.commit()

    return MessageResponse(
        detail = 'email confirmed'
    )



@router.post(
        '/login', 
        tags=['auth'], 
        response_model=TokenResponse
)
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
    ):

    result = await db.execute(
        select(UserBase).where(
            UserBase.email == user.email
        )
    )

    log_user = result.scalar_one_or_none()
    
    if not log_user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'User does not exist'
        )

    if not verify_password(user.password, log_user.hashed_password):
        raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = 'password is incorrect'
                )
    
    check_user_active(user=log_user)
    check_user_verified_email(user=log_user)

    token_response = generate_tokens(
        user_id=log_user.id,
        db=db
    )

    await db.commit()

    return token_response


@router.post('/refresh', response_model=TokenResponse)
async def refresh(
    token: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):

    user_id, refresh_token_db = await validate_refresh_token(
        token=token.refresh_token,
        db=db
    )

    tokens = generate_tokens(
        user_id=user_id,
        db=db
    )

    revoke_refresh_token(refresh_token_db=refresh_token_db)

    await db.commit()

    return tokens


@router.post('/logout', tags=['auth', 'logout'])
async def logout(
    token: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    
    _, refresh_token_db = await validate_refresh_token(
        token=token.refresh_token,
        db=db
    )

    revoke_refresh_token(refresh_token_db=refresh_token_db)

    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    ) 


@router.post('/logout/all', tags=['auth', 'logout'])
async def logout_all(
    user: UserBase = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    await db.execute(
        update(RefreshTokenBase)
        .where(
            RefreshTokenBase.user_id == user.id,
            RefreshTokenBase.revoked.is_(False)
        )
        .values(revoked=True)
    )   

    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )