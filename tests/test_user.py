from tests.helpers import (
    DEFAULT_USER,
    register_user,
    login_user,
    get_access_token,
    get_refresh_token,
    auth_headers,
    logout_user,
    refresh_user,
    get_users_me
)

# ---------- GET USERS/ME ----------
def test_users_me_success(client):
    register_response = register_user(client)

    response = get_users_me(client, get_access_token(register_response))

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data["id"], int)
    assert data['email'] == DEFAULT_USER["email"]
    assert data['name'] == DEFAULT_USER["name"]
    assert data['is_private'] is False


def test_users_me_invalid_token(client):
    response = get_users_me(client, 'secret.invalid_token')

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token'


def test_users_me_logout_then_usersme(client):
    register_response = register_user(client)

    logout_user(client, get_refresh_token(register_response))

    response = get_users_me(client, get_access_token(register_response))

    assert response.status_code == 200


def test_users_me_refresh_then_usersme(client):
    register_response = register_user(client)

    refresh_response = refresh_user(client, get_refresh_token(register_response))

    response = get_users_me(client, get_access_token(refresh_response))

    assert response.status_code == 200


def test_users_me_deleted_user(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    client.delete("/users/me", headers=auth_headers(access_token))

    response = get_users_me(client, access_token)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


def test_users_me_refresh_instead(client):
    register_response = register_user(client)

    response = get_users_me(client, get_refresh_token(register_response))

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


def test_users_me_without_authorization(client):
    response = client.get('/users/me')

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'


# ---------- PATCH USERS/ME ----------