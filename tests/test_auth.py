import pytest

from tests.helpers.requests import (
    register_user,
    login_user,
    refresh_user,
    logout_user,
    get_access_token,
    get_refresh_token,
    auth_headers,
    delete_refresh_token_from_db
)

from tests.helpers.assertions import assert_tokens

# ---------- REGISTER ----------

@pytest.mark.asyncio
async def test_register_success(client):
    response = await register_user(client)

    assert response.status_code == 200

    assert_tokens(response.json())


@pytest.mark.asyncio
async def test_register_existing_email(client):
    await register_user(client)
    response = await register_user(client)

    assert response.status_code == 400
    assert response.json()['detail'] == "User already exists"


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await register_user(client, email='just_email')

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    response = await register_user(client, password='1')

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_name(client):
    response = await register_user(client, name=' ')

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_without_name(client):
    response = await register_user(client, name=None)

    assert response.status_code == 422


# ---------- LOGIN ----------

@pytest.mark.asyncio
async def test_login_success(client):
    await register_user(client)

    response = await login_user(client)

    assert response.status_code == 200

    assert_tokens(response.json())


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await register_user(client)

    response = await login_user(client, password='87654321')

    assert response.status_code == 401
    assert response.json()['detail'] == 'password is incorrect'


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    response = await login_user(client)

    assert response.status_code == 404
    assert response.json()['detail'] == 'User does not exist'


@pytest.mark.asyncio
async def test_login_deleted_user(client):
    register_response = await register_user(client)
    
    await client.delete(
        '/users/me', 
        headers=auth_headers(get_access_token(register_response))
        )

    response = await login_user(client)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


# ---------- REFRESH ----------
@pytest.mark.asyncio
async def test_refresh_success(client):
    register_response = await register_user(client)

    old_refresh_token = get_refresh_token(register_response)
    old_access_token = get_access_token(register_response)

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
async def test_refresh_access_instead_refresh_token(client):
    register_response = await register_user(client)

    response = await refresh_user(client, get_access_token(register_response))

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


@pytest.mark.asyncio
async def test_refresh_with_revoked_token(client):
    register_response = await register_user(client)

    await refresh_user(client, get_refresh_token(register_response))

    response = await refresh_user(client, get_refresh_token(register_response))

    assert response.status_code == 403
    assert response.json()['detail'] == 'token is inactive'


@pytest.mark.asyncio
async def test_refresh_unknown_refresh_token(client, db):
    register_response = await register_user(client)

    refresh_token = get_refresh_token(register_response)

    await delete_refresh_token_from_db(db, refresh_token)

    response = await refresh_user(client, refresh_token)

    assert response.status_code == 401
    assert response.json()['detail'] == "invalid refresh token"


@pytest.mark.asyncio
async def test_logout_then_refresh(client):
    register_response = await register_user(client)

    await logout_user(client, get_refresh_token(register_response))

    response = await refresh_user(client,  get_refresh_token(register_response))

    assert response.status_code == 403
    assert response.json()['detail'] == "token is inactive"

# ---------- LOGOUT ----------
@pytest.mark.asyncio
async def test_logout_success(client):
    register_response = await register_user(client)

    response = await logout_user(client, get_refresh_token(register_response))
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_twice(client):
    register_response = await register_user(client)

    await logout_user(client, get_refresh_token(register_response))

    response = await logout_user(client, get_refresh_token(register_response))

    assert response.status_code == 403
    assert response.json()['detail'] == 'token is inactive'


@pytest.mark.asyncio
async def test_logout_invalid_token(client):
    response = await logout_user(client, 'key.broken_refresh.sign')

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token'


@pytest.mark.asyncio
async def test_logout_access_token(client):
    register_response = await register_user(client)

    response = await logout_user(client, get_access_token(register_response))

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


@pytest.mark.asyncio
async def test_logout_unknown_refresh_token(client, db):
    register_response = await register_user(client)

    refresh_token = get_refresh_token(register_response)

    await delete_refresh_token_from_db(db, refresh_token)

    response = await logout_user(client, refresh_token)

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid refresh token"


# ---------- LOGOUT/ALL ----------
@pytest.mark.asyncio
async def test_logout_all_success(client):
    register_response = await register_user(client)

    tokens = [
        get_refresh_token(register_response),
        get_refresh_token(await login_user(client)),
        get_refresh_token(await login_user(client)),
        get_refresh_token(await login_user(client)),
    ]

    response = await client.post(
        '/logout/all', 
        headers=auth_headers(get_access_token(register_response))
    )

    assert response.status_code == 204

    for token in tokens:
        response = await refresh_user(client, token)

        assert response.status_code == 403
        assert response.json()["detail"] == "token is inactive"


@pytest.mark.asyncio
async def test_logout_all_invalid_access_token(client):
    response = await client.post(
        '/logout/all', 
        headers=auth_headers("secret.broken.token"))

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token'



