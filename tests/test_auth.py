import pytest

from unittest.mock import AsyncMock
from sqlalchemy import select

from tests.helpers.requests import (
    register_user,
    login_user,
    refresh_user,
    logout_user,
    get_refresh_token,
    auth_headers,
    delete_refresh_token_from_db,
    get_email_token_from_db, 
    delete_email_token_from_db,
)
from tests.helpers.assertions import assert_tokens
from tests.helpers.data import DEFAULT_USER

from app.database.models import UserBase, EmailTokenBase
from app.core.email import hash_email_token

from app.core.email import hash_email_token
from app.core.settings import settings
from datetime import datetime, timedelta, timezone

from app.services.user import get_user_by_email

# ---------- REGISTER ----------

@pytest.mark.asyncio
async def test_register_success(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    response = await register_user(client)

    assert response.status_code == 201
    assert response.json()["detail"] == (
        "Registration successful. Check your email."
    )

    result = await db.execute(
        select(UserBase).where(
            UserBase.email == DEFAULT_USER["email"]
        )
    )
    user = result.scalar_one()

    assert user.email_verified is False
    assert user.is_active is True

    send_email_mock.assert_awaited_once_with(
        recipient=user.email,
        user_name=user.name,
        token=send_email_mock.await_args.kwargs["token"]
    )

    token = send_email_mock.await_args.kwargs["token"]

    result = await db.execute(
        select(EmailTokenBase).where(
            EmailTokenBase.user_id == user.id,
            EmailTokenBase.purpose == "email_verification"
        )
    )
    email_token = result.scalar_one()

    assert email_token.token_hash == hash_email_token(token)
    assert email_token.used_at is None
    assert email_token.expires_at > email_token.created_at


@pytest.mark.asyncio
async def test_register_existing_email(client, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    first_response = await register_user(client)
    assert first_response.status_code == 201

    response = await register_user(client)

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

    send_email_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await register_user(client, email="just_email")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    response = await register_user(client, password="1")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_name(client):
    response = await register_user(client, name=" ")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_without_name(client):
    response = await register_user(client, name=None)

    assert response.status_code == 422


# ---------- RESEND-VERIFICATION ----------

@pytest.mark.asyncio
async def test_resend_verification_success(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)

    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()
    token = send_email_mock.await_args.kwargs["token"]

    result = await db.execute(
        select(EmailTokenBase).where(
            EmailTokenBase.token_hash == hash_email_token(token)
        )
    )

    token_from_db = result.scalar_one()

    token_from_db.created_at = datetime.now(timezone.utc) - timedelta(seconds=settings.RESEND_VERIFICATION_COOLDOWN_SECONDS + 1)

    await db.flush()

    response = await client.post(
        '/auth/resend-verification',
        json={'email': DEFAULT_USER['email']}
    )

    assert response.status_code == 200
    assert response.json()['detail'] == 'Verification email sent. Check your email.'
    assert send_email_mock.await_count == 2


@pytest.mark.asyncio
async def test_resend_verification_already_verified_user(client, authenticated_user):
    user_data = await authenticated_user()

    response = await client.post(
        '/auth/resend-verification',
        json={'email': user_data['user'].email}
    )

    assert response.status_code == 409
    assert response.json()['detail'] == 'email is already verified'


@pytest.mark.asyncio
async def test_resend_verification_user_not_found(client):
    response = await client.post(
        '/auth/resend-verification',
        json={'email': DEFAULT_USER['email']}
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'User does not exist'


@pytest.mark.asyncio
async def test_resend_verification_within_cooldown(client, monkeypatch):    
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)

    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()

    response = await client.post(
        '/auth/resend-verification',
        json={'email': DEFAULT_USER['email']}
    )

    assert response.status_code == 429
    assert response.json()['detail'] == 'Please wait before requesting another email'


# ---------- VERIFY-EMAIL ----------

@pytest.mark.asyncio
async def test_verify_email_success(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)
    
    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()
    token = send_email_mock.await_args.kwargs["token"]

    response = await client.get(
        "/auth/verify-email",
        params={"token": token}
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "email confirmed"

    result = await db.execute(
        select(UserBase).where(
            UserBase.email == DEFAULT_USER["email"]
        )
    )
    user = result.scalar_one()

    assert user.email_verified is True

    token_hash = hash_email_token(token)

    result = await db.execute(
        select(EmailTokenBase).where(
            EmailTokenBase.token_hash == token_hash
        )
    )

    email_token = result.scalar_one()

    assert email_token.used_at is not None


@pytest.mark.asyncio
async def test_verify_email_expired_token(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)
    
    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()
    token = send_email_mock.await_args.kwargs["token"]

    result = await db.execute(
        select(EmailTokenBase).where(
            EmailTokenBase.token_hash == hash_email_token(token)
        )
    )

    token_from_db = result.scalar_one()

    token_from_db.expires_at = datetime.now(timezone.utc) - timedelta(minutes=settings.EMAIL_TOKEN_EXPIRE_MINUTES + 1)

    await db.flush()

    response = await client.get(
        '/auth/verify-email',
        params={"token": token}
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'Token has expired'


@pytest.mark.asyncio
async def test_verify_email_no_token_in_db(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)
    
    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()
    token = send_email_mock.await_args.kwargs["token"]

    await delete_email_token_from_db(db, token)

    response = await client.get(
        '/auth/verify-email',
        params={"token": token}
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid token'


@pytest.mark.asyncio
async def test_verify_email_incorrect_purpose(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)
    
    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()
    token = send_email_mock.await_args.kwargs["token"]

    token_from_db = await get_email_token_from_db(db, token)

    token_from_db.purpose = "incorrect_purpose"

    await db.flush()

    response = await client.get(
        '/auth/verify-email',
        params={"token": token}
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid token purpose'


@pytest.mark.asyncio
async def test_verify_email_used_token(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)
    
    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()
    token = send_email_mock.await_args.kwargs["token"]

    token_from_db = await get_email_token_from_db(db, token)

    token_from_db.used_at = datetime.now(timezone.utc)

    await db.flush()

    response = await client.get(
        '/auth/verify-email',
        params={"token": token}
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Token has already been used'


@pytest.mark.asyncio
async def test_verify_email_already_verified_user(client, db, monkeypatch):
    send_email_mock = AsyncMock()

    monkeypatch.setattr(
        "app.api.auth.send_verification_email",
        send_email_mock
    )

    register_response = await register_user(client)
    
    assert register_response.status_code == 201

    send_email_mock.assert_awaited_once()
    token = send_email_mock.await_args.kwargs["token"]

    user = await get_user_by_email(db, DEFAULT_USER['email'])

    user.email_verified = True

    await db.flush()

    response = await client.get(
        '/auth/verify-email',
        params={"token": token}
    )

    assert response.status_code == 409
    assert response.json()['detail'] == 'Email is already verified'
    
# ---------- LOGIN ----------

@pytest.mark.asyncio
async def test_login_success(client, authenticated_user):
    await authenticated_user()

    response = await login_user(client)

    assert response.status_code == 200

    assert_tokens(response.json())


@pytest.mark.asyncio
async def test_login_wrong_password(client, authenticated_user):
    await authenticated_user()

    response = await login_user(client, password='87654321')

    assert response.status_code == 401
    assert response.json()['detail'] == 'password is incorrect'


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    response = await login_user(client)

    assert response.status_code == 404
    assert response.json()['detail'] == 'User does not exist'


@pytest.mark.asyncio
async def test_login_deleted_user(client, authenticated_user):
    user_data = await authenticated_user()
    
    delete_response = await client.delete(
        '/users/me', 
        headers=auth_headers(user_data['access_token'])
        )

    assert delete_response.status_code == 204

    response = await login_user(client)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


# ---------- REFRESH ----------
@pytest.mark.asyncio
async def test_refresh_success(client, authenticated_user):
    user_data = await authenticated_user()

    old_refresh_token = user_data['refresh_token']
    old_access_token = user_data['access_token']

    response = await refresh_user(client, old_refresh_token)

    assert response.status_code == 200

    data = response.json()

    assert_tokens(data)

    assert old_refresh_token != data['refresh_token']
    assert old_access_token != data['access_token']


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    response = await refresh_user(client, "key.broken_refresh.sign")

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid token"


@pytest.mark.asyncio
async def test_refresh_access_instead_refresh_token(client, authenticated_user):
    user_data = await authenticated_user()

    response = await refresh_user(client, user_data['access_token'])

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


@pytest.mark.asyncio
async def test_refresh_with_revoked_token(client, authenticated_user):
    user_data = await authenticated_user()

    await refresh_user(client, user_data['refresh_token'])

    response = await refresh_user(client, user_data['refresh_token'])

    assert response.status_code == 403
    assert response.json()['detail'] == 'token is inactive'


@pytest.mark.asyncio
async def test_refresh_unknown_refresh_token(client, db, authenticated_user):
    user_data = await authenticated_user()

    refresh_token = user_data['refresh_token']

    await delete_refresh_token_from_db(db, refresh_token)

    response = await refresh_user(client, refresh_token)

    assert response.status_code == 401
    assert response.json()['detail'] == "invalid refresh token"


@pytest.mark.asyncio
async def test_logout_then_refresh(client, authenticated_user):
    user_data = await authenticated_user()

    await logout_user(client, user_data['refresh_token'])

    response = await refresh_user(client, user_data['refresh_token'])

    assert response.status_code == 403
    assert response.json()['detail'] == "token is inactive"

# ---------- LOGOUT ----------
@pytest.mark.asyncio
async def test_logout_success(client, authenticated_user):
    user_data = await authenticated_user()

    response = await logout_user(client, user_data['refresh_token'])
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_twice(client, authenticated_user):
    user_data = await authenticated_user()

    await logout_user(client, user_data['refresh_token'])

    response = await logout_user(client, user_data['refresh_token'])

    assert response.status_code == 403
    assert response.json()['detail'] == 'token is inactive'


@pytest.mark.asyncio
async def test_logout_invalid_token(client):
    response = await logout_user(client, 'key.broken_refresh.sign')

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token'


@pytest.mark.asyncio
async def test_logout_access_token(client, authenticated_user):
    user_data = await authenticated_user()

    response = await logout_user(client, user_data['access_token'])

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


@pytest.mark.asyncio
async def test_logout_unknown_refresh_token(client, db, authenticated_user):
    user_data = await authenticated_user()

    await delete_refresh_token_from_db(db, user_data['refresh_token'])

    response = await logout_user(client, user_data['refresh_token'])

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid refresh token"


# ---------- LOGOUT/ALL ----------
@pytest.mark.asyncio
async def test_logout_all_success(client, authenticated_user):
    user_data = await authenticated_user()

    tokens = [
        user_data['refresh_token'],
        get_refresh_token(await login_user(client)),
        get_refresh_token(await login_user(client)),
        get_refresh_token(await login_user(client)),
    ]

    response = await client.post(
        '/auth/logout/all', 
        headers=auth_headers(user_data['access_token'])
    )

    assert response.status_code == 204

    for token in tokens:
        response = await refresh_user(client, token)

        assert response.status_code == 403
        assert response.json()["detail"] == "token is inactive"


@pytest.mark.asyncio
async def test_logout_all_invalid_access_token(client):
    response = await client.post(
        '/auth/logout/all', 
        headers=auth_headers("secret.broken.token"))

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token'



