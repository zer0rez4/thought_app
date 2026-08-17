from tests.helpers.data import DEFAULT_USER

from tests.helpers.requests import (
    login_user,
    get_access_token,
    
    logout_user,
    refresh_user,
    get_users_me,
    update_user,
    delete_user,
    restore_user,
    get_user,

    create_thought
)

from app.database.models import UserBase

# ---------- GET USERS/ME ----------
def test_users_me_success(client, registered_user):
    response = get_users_me(client, registered_user['access_token'])

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data["id"], int)
    assert data['email'] == DEFAULT_USER["email"]
    assert data['name'] == DEFAULT_USER["name"]
    assert data['is_private'] is False


def test_users_me_logout_then_usersme(client, registered_user):
    logout_user(client, registered_user['refresh_token'])

    response = get_users_me(client, registered_user['access_token'])

    assert response.status_code == 200


def test_users_me_refresh_then_usersme(client, registered_user):
    refresh_response = refresh_user(client, registered_user['refresh_token'])

    response = get_users_me(client, get_access_token(refresh_response))

    assert response.status_code == 200


def test_users_me_deleted_user(client, registered_user):
    delete_user(client, registered_user['access_token'])

    response = get_users_me(client, registered_user['access_token'])

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


def test_users_me_refresh_instead_access(client, registered_user):
    response = get_users_me(client, registered_user['refresh_token'])

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


def test_users_me_without_authorization(client):
    response = client.get('/users/me')

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'


# ---------- PATCH USERS/ME ----------
def test_users_me_change_name_success(client, registered_user):
    response = update_user(
        client,
        registered_user['access_token'],
        new_name="new_name_test"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "new_name_test"
    assert data["is_private"] is False


def test_users_me_change_privacy_success(client, registered_user):
    response = update_user(
        client,
        registered_user['access_token'],
        is_private=True
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == DEFAULT_USER["name"]
    assert data["is_private"] is True


def test_users_me_change_name_and_privacy_success(client, registered_user):
    response = update_user(
        client,
        registered_user['access_token'],
        new_name="new_name_test",
        is_private=True
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "new_name_test"
    assert data["is_private"] is True


def test_users_me_update_without_changes(client, registered_user):
    response = update_user(
        client,
        registered_user['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == DEFAULT_USER["name"]
    assert data["is_private"] is False


def test_users_me_invalid_name(client, registered_user):
    response = update_user(
        client, 
        registered_user['access_token'],
        new_name="    "
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["loc"] == ["body", "new_name"]
    assert "The name can not be empty" in error["msg"]


def test_users_me_invalid_is_private(client, registered_user):
    response = update_user(
        client,
        registered_user['access_token'],
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


# ---------- DELETE USERS/ME ----------
def test_delete_user_success(client, db, registered_user):
    response = delete_user(client, registered_user['access_token'])

    assert response.status_code == 204

    db.expire_all()

    user = db.query(UserBase).filter(
        UserBase.id == registered_user["user"].id
    ).first()

    assert user.is_active is False


def test_delete_user_already_deleted(client, registered_user):
    delete_user(client, registered_user['access_token'])

    response = delete_user(client, registered_user['access_token'])

    assert response.status_code == 403
    assert response.json()["detail"] == "account is deleted"


def test_delete_user_login_after_delete(client, registered_user):
    delete_user(client, registered_user['access_token'])

    response = login_user(client)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


# ---------- POST USERS/RESTORE ----------
def test_users_restore_success(client, db, registered_user):
    delete_user(client, registered_user['access_token'])

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


def test_users_restore_user_is_active(client, registered_user):
    response = restore_user(client)

    assert response.status_code == 409
    assert response.json()['detail'] == 'account is already active'


def test_users_restore_wrong_password(client, registered_user):
    delete_user(client, registered_user['access_token'])

    response = restore_user(client, password="wrong_password")

    assert response.status_code == 401
    assert response.json()["detail"] == "password is incorrect"


# ---------- GET USERS/{USER_ID} ----------
def test_get_users_userid_success(client, created_two_users):
    create_thought(
        client,
        created_two_users["first"]["access_token"],
        text="PUBLIC THOUGHT 1",
        is_public=True
    )

    create_thought(
        client,
        created_two_users["first"]["access_token"],
        text="PUBLIC THOUGHT 2",
        is_public=True
    )

    response = get_user(
        client, 
        created_two_users["second"]["access_token"],
        user_id=created_two_users["first"]["user"].id
    )

    assert response.status_code == 200

    data = response.json()

    assert data['name'] == DEFAULT_USER["name"]

    thoughts = data["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2

    assert thoughts["items"][0]["text"] == "PUBLIC THOUGHT 1"
    assert thoughts["items"][1]["text"] == "PUBLIC THOUGHT 2"


def test_get_users_userid_wrong_id(client, registered_user):
    response = get_user(
        client,
        registered_user['access_token'],
        user_id=9999
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'user not found'


def test_get_users_userid_private_account(client, created_two_users):
    update_user(
        client,
        created_two_users['first']['access_token'],
        is_private=True
    )

    response = get_user(
        client, 
        created_two_users['second']['access_token'],
        user_id=created_two_users['first']['user'].id
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is private'


def test_get_users_userid_private_account_owner(client, registered_user):
    update_user(
        client,
        registered_user['access_token'],
        is_private=True
    )

    response = get_user(
        client,
        registered_user['access_token'],
        user_id=registered_user['user'].id
    )

    assert response.status_code == 200


def test_get_users_userid_check_only_public_thoughts(client, created_two_users):
    create_thought(
        client,
        created_two_users['first']['access_token'],
        is_public=False
    )

    create_thought(
        client,
        created_two_users['first']['access_token']
    )

    response = get_user(
        client,
        created_two_users['second']['access_token'],
        user_id=created_two_users['first']['user'].id
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 1
    assert len(thoughts["items"]) == 1
    assert thoughts["items"][0]["is_public"] is True


def test_get_users_userid_public_private_owner(client, registered_user):
    access_token = registered_user['access_token']
    
    create_thought(
        client,
        access_token,
        is_public=False
    )

    create_thought(
        client,
        access_token
    )

    response = get_user(
        client, 
        access_token,
        user_id=registered_user['user'].id
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2


def test_get_users_userid_user_without_thoughts(client, created_two_users):
    response = get_user(
        client,
        created_two_users['second']['access_token'],
        user_id=created_two_users['first']['user'].id
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 0
    assert len(thoughts["items"]) == 0


def test_get_users_userid_search(client, created_two_users):
    access_token = created_two_users['first']['access_token']

    for thought_text in ["search check", "SEARCH check", "TEST"]:
        create_thought(
            client,
            access_token,
            text=thought_text
        )

    response = get_user(
        client,
        created_two_users['second']['access_token'],
        user_id=created_two_users['first']['user'].id,
        search="search"
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2

    assert thoughts["items"][0]["text"] == "search check"
    assert thoughts["items"][1]["text"] == "SEARCH check"


def test_get_users_userid_search_no_results(client, created_two_users):
    access_token = created_two_users['first']['access_token']

    for thought_text in ["search check", "SEARCH check", "TEST"]:
        create_thought(
            client,
            access_token,
            text=thought_text
        )

    response = get_user(
        client,
        created_two_users['second']['access_token'],
        user_id=created_two_users['first']['user'].id,
        search="fortnite"
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 0
    assert len(thoughts["items"]) == 0


def test_get_users_userid_pagination(client, registered_user):
    access_token = registered_user['access_token']

    for _ in range(5):
        create_thought(
            client,
            access_token
        )

    response = get_user(
        client,
        access_token,
        user_id=registered_user['user'].id,
        limit=2,
        offset=2
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 5
    assert thoughts["items"][0]["id"] == 3
    assert thoughts["items"][1]["id"] == 4
    assert thoughts["has_next"] is True