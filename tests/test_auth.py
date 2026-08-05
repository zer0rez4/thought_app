from tests.helpers import (
    register_user,
    login_user,
    assert_tokens,
    refresh_user
)

# ---------- REGISTER ----------

def test_register_success(client):
    response = register_user(client)

    assert response.status_code == 200

    assert_tokens(response.json())


def test_register_existing_email(client):
    register_user(client)
    response = register_user(client)

    assert response.status_code == 400
    assert response.json()['detail'] == "User already exists"


def test_register_invalid_email(client):
    response = register_user(client, email='just_email')

    assert response.status_code == 422


def test_register_short_password(client):
    response = register_user(client, password='1')

    assert response.status_code == 422


def test_register_invalid_name(client):
    response = register_user(client, name=' ')

    assert response.status_code == 422


def test_register_without_name(client):
    response = register_user(client, name=None)

    assert response.status_code == 422


# ---------- LOGIN ----------

def test_login_success(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200

    assert_tokens(response.json())


def test_login_wrong_password(client):
    register_user(client)

    response = login_user(client, password='87654321')

    assert response.status_code == 401
    assert response.json()['detail'] == 'password is incorrect'


def test_login_unknown_user(client):
    response = login_user(client)

    assert response.status_code == 404
    assert response.json()['detail'] == 'User does not exist'


def test_login_deleted_user(client):
    register_response = register_user(client)
    
    access_token = register_response.json()['access_token']
    
    client.delete(
        '/users/me', 
        headers={
            "Authorization": f"Bearer {access_token}"
            }
        )

    response = login_user(client)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


# ---------- REFRESH ----------
def test_refresh_success(client):
    register_response = register_user(client)

    old_refresh_token = register_response.json()['refresh_token']
    old_access_token = register_response.json()['access_token']

    response = refresh_user(client, old_refresh_token)

    assert response.status_code == 200

    data = response.json()

    assert_tokens(data)

    assert old_refresh_token != data['refresh_token']
    assert old_access_token != data['access_token']


def test_refresh_broken_token(client):
    register_user(client)

    response = refresh_user(client, "key.broken_refresh.sign")

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid token"


def test_refresh_empty_token(client):
    response = refresh_user(client, " ")

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid token"


def test_refresh_access_instead_refresh_token(client):
    register_response = register_user(client)

    response = refresh_user(client, register_response.json()['access_token'])

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


def test_refresh_with_revoked_token(client):
    register_response = register_user(client)

    refresh_user(client, register_response.json()['refresh_token'])

    response = refresh_user(client, register_response.json()['refresh_token'])

    assert response.status_code == 403
    assert response.json()['detail'] == 'token is inactive'

