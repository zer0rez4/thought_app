from tests.helpers import (
    DEFAULT_USER,
    register_user,
    login_user,
    get_access_token,
    get_refresh_token,
    auth_headers,
    
    logout_user,
    refresh_user,
    get_users_me,
    update_user,
    delete_user,
    restore_user,

    create_thought
)
from app.database.models import UserBase

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
def test_users_me_change_name_success(client):
    register_reponse = register_user(client)

    response = update_user(
        client,
        get_access_token(register_reponse),
        new_name="new_name_test"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "new_name_test"
    assert data["is_private"] == False


def test_users_me_change_privaty_success(client):
    register_reponse = register_user(client)

    response = update_user(
        client,
        get_access_token(register_reponse),
        is_private=True
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == DEFAULT_USER["name"]
    assert data["is_private"] == True


def test_users_me_change_name_and_privaty_success(client):
    register_reponse = register_user(client)

    response = update_user(
        client,
        get_access_token(register_reponse),
        new_name="new_name_test",
        is_private=True
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "new_name_test"
    assert data["is_private"] == True


def test_users_me_update_without_changes(client):
    register_reponse = register_user(client)

    response = update_user(
        client,
        get_access_token(register_reponse)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == DEFAULT_USER["name"]
    assert data["is_private"] == False


def test_users_me_invalid_name(client):
    register_reponse = register_user(client)

    response = update_user(
        client, 
        get_access_token(register_reponse),
        new_name="    "
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["loc"] == ["body", "new_name"]
    assert "The name can not be empty" in error["msg"]


def test_users_me_invalid_is_private(client):
    register_reponse = register_user(client)

    response = update_user(
        client,
        get_access_token(register_reponse),
        is_private="not_boolean"
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "is_private"]


def test_users_me_without_auth(client):
    response = update_user(
        client
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'


def test_users_me_refresh_instead_access(client):
    register_response = register_user(client)

    response = update_user(
        client,
        get_refresh_token(register_response)
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


# ---------- DELETE USERS/ME ----------
def test_delete_user_success(client, db):
    register_response = register_user(client)

    response = delete_user(client, get_access_token(register_response))

    assert response.status_code == 204

    user = db.query(UserBase).filter(
        UserBase.email == DEFAULT_USER["email"]
    ).first()

    assert user.is_active is False


def test_delete_user_already_deleted(client):
    register_response = register_user(client)

    delete_user(client, get_access_token(register_response))

    response = delete_user(client, get_access_token(register_response))

    assert response.status_code == 403
    assert response.json()["detail"] == "account is deleted"


def test_delete_user_login_after_delete(client):
    register_response = register_user(client)

    delete_user(client, get_access_token(register_response))

    response = login_user(client)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


# ---------- POST USERS/RESTORE ----------
def test_users_restore_success(client, db):
    register_response = register_user(client)

    delete_user(client, get_access_token(register_response))

    response = restore_user(client)

    assert response.status_code == 200

    user = db.query(UserBase).filter(
        UserBase.email == DEFAULT_USER["email"]
    ).first()

    assert user.is_active is True


def test_users_restore_user_not_exist(client):
    response = restore_user(client)

    assert response.status_code == 404
    assert response.json()['detail'] == 'User does not exist'


def test_users_restore_user_is_active(client):
    register_user(client)

    response = restore_user(client)

    assert response.status_code == 409
    assert response.json()['detail'] == 'account is already active'


def test_users_restore_wrong_password(client):
    register_response = register_user(client)

    delete_user(client, get_access_token(register_response))

    response = restore_user(client, password="wrong_password")

    assert response.status_code == 401
    assert response.json()["detail"] == "password is incorrect"


# ---------- GET USERS/{USER_ID} ----------
def test_get_users_userid_success(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='TEST2@gmail.com', name="TEST2")

    create_thought(
        client,
        get_access_token(register_response1),
        text="PUBLIC THOUGHT 1",
        is_public=True
    )

    create_thought(
        client,
        get_access_token(register_response1),
        text="PUBLIC THOUGHT 2",
        is_public=True
    )

    response = client.get(
        "/users/1", 
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 200

    data = response.json()

    assert data['name'] == DEFAULT_USER["name"]

    thoughts = data["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2

    assert thoughts["items"][0]["text"] == "PUBLIC THOUGHT 1"
    assert thoughts["items"][1]["text"] == "PUBLIC THOUGHT 2"


def test_get_users_userid_wrong_id(client):
    register_response = register_user(client)

    response = client.get(
        "/users/2",
        headers=auth_headers(get_access_token(register_response))
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'user not found'


def test_get_users_userid_private_account(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='TEST2@gmail.com', name="TEST2")

    update_user(
        client,
        get_access_token(register_response1),
        is_private=True
    )

    response = client.get(
        "/users/1",
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is private'


def test_get_users_userid_private_account_owner(client):
    register_response = register_user(client)

    update_user(
        client,
        get_access_token(register_response),
        is_private=True
    )

    response = client.get(
        "/users/1",
        headers=auth_headers(get_access_token(register_response))
    )

    assert response.status_code == 200


def test_get_users_userid_check_only_public_thoughts(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='TEST2@gmail.ru')

    create_thought(
        client,
        get_access_token(register_response1),
        is_public=False
    )

    create_thought(
        client,
        get_access_token(register_response1)
    )

    response = client.get(
        "/users/1",
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 1
    assert len(thoughts["items"]) == 1
    assert thoughts["items"][0]["is_public"] == True


def test_get_users_userid_public_private_owner(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)
    
    create_thought(
        client,
        access_token,
        is_public=False
    )

    create_thought(
        client,
        access_token
    )

    response = client.get(
        "/users/1",
        headers=auth_headers(access_token)
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2


def test_get_users_userid_user_without_thoughts(client):
    register_user(client)
    register_response2 = register_user(client, email='TEST2@gmail.ru')

    response = client.get(
        "/users/1",
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 0
    assert len(thoughts["items"]) == 0


def test_get_users_userid_search(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='TEST2@gmail.ru')

    create_thought(
        client,
        get_access_token(register_response1),
        text="search check"
    )

    create_thought(
        client,
        get_access_token(register_response1),
        text="SEARCH check"
    )

    create_thought(
        client,
        get_access_token(register_response1),
        text="TEST"
    )

    response = client.get(
        "/users/1",
        params={
            "search": "search"
        },
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2

    assert thoughts["items"][0]["text"] == "search check"
    assert thoughts["items"][1]["text"] == "SEARCH check"


def test_get_users_userid_search_no_results(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='TEST2@gmail.ru')

    create_thought(
        client,
        get_access_token(register_response1),
        text="search check"
    )

    create_thought(
        client,
        get_access_token(register_response1),
        text="SEARCH check"
    )

    create_thought(
        client,
        get_access_token(register_response1),
        text="TEST"
    )

    response = client.get(
        "/users/1",
        params={
            "search": "fortnite"
        },
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 0
    assert len(thoughts["items"]) == 0


def test_get_users_userid_pagination(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    for _ in range(5):
        create_thought(
            client,
            access_token
        )

    response = client.get(
        "/users/1",
        params={
            "limit": 2,
            "offset": 2
        },
        headers=auth_headers(access_token)
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 5
    assert thoughts["items"][0]["id"] == 3
    assert thoughts["items"][1]["id"] == 4
    assert thoughts["has_next"] is True