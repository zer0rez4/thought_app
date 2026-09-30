import pytest

from sqlalchemy import select

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
    get_user
)

from app.database.models import UserBase

# ---------- GET USERS/ME ----------

@pytest.mark.asyncio
async def test_users_me_success(client, authenticated_user):
    user = await authenticated_user()

    response = await get_users_me(client, user['access_token'])

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data["id"], int)
    assert data['email'] == DEFAULT_USER["email"]
    assert data['name'] == DEFAULT_USER["name"]
    assert data['is_private'] is False


@pytest.mark.asyncio
async def test_users_me_logout_then_usersme(client, authenticated_user):
    user = await authenticated_user()

    await logout_user(client, user['refresh_token'])

    response = await get_users_me(client, user['access_token'])

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_users_me_refresh_then_usersme(client, authenticated_user):
    user = await authenticated_user()

    refresh_response = await refresh_user(client, user['refresh_token'])

    response = await get_users_me(client, get_access_token(refresh_response))

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_users_me_deleted_user(client, authenticated_user):
    user = await authenticated_user()

    await delete_user(client, user['access_token'])

    response = await get_users_me(client, user['access_token'])

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


@pytest.mark.asyncio
async def test_users_me_refresh_instead_access(client, authenticated_user):
    user = await authenticated_user()

    response = await get_users_me(client, user['refresh_token'])

    assert response.status_code == 401
    assert response.json()['detail'] == 'invalid token type'


@pytest.mark.asyncio
async def test_users_me_without_authorization(client):
    response = await client.get('/users/me')

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'


# ---------- PATCH USERS/ME ----------

@pytest.mark.asyncio
async def test_users_me_change_name_success(client, authenticated_user):
    user = await authenticated_user()

    response = await update_user(
        client,
        user['access_token'],
        new_name="new_name_test"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "new_name_test"
    assert data["is_private"] is False


@pytest.mark.asyncio
async def test_users_me_change_privacy_success(client, authenticated_user):
    user = await authenticated_user()

    response = await update_user(
        client,
        user['access_token'],
        is_private=True
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == DEFAULT_USER["name"]
    assert data["is_private"] is True


@pytest.mark.asyncio
async def test_users_me_change_name_and_privacy_success(client, authenticated_user):
    user = await authenticated_user()

    response = await update_user(
        client,
        user['access_token'],
        new_name="new_name_test",
        is_private=True
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "new_name_test"
    assert data["is_private"] is True


@pytest.mark.asyncio
async def test_users_me_update_without_changes(client, authenticated_user):
    user = await authenticated_user()

    response = await update_user(
        client,
        user['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == DEFAULT_USER["name"]
    assert data["is_private"] is False


@pytest.mark.asyncio
async def test_users_me_invalid_name(client, authenticated_user):
    user = await authenticated_user()

    response = await update_user(
        client, 
        user['access_token'],
        new_name="    "
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["loc"] == ["body", "new_name"]
    assert "The name can not be empty" in error["msg"]


@pytest.mark.asyncio
async def test_users_me_invalid_is_private(client, authenticated_user):
    user = await authenticated_user()

    response = await update_user(
        client,
        user['access_token'],
        is_private="not_boolean"
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "is_private"]


@pytest.mark.asyncio
async def test_users_me_without_auth(client):
    response = await update_user(
        client
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'


# ---------- DELETE USERS/ME ----------
@pytest.mark.asyncio
async def test_delete_user_success(client, db, authenticated_user):
    auth_user = await authenticated_user()

    response = await delete_user(client, auth_user['access_token'])

    assert response.status_code == 204

    result = await db.execute(
        select(UserBase)
        .where(UserBase.id == auth_user["user"].id)
    )

    user = result.scalar_one_or_none()

    assert user.is_active is False


@pytest.mark.asyncio
async def test_delete_user_already_deleted(client, authenticated_user):
    user = await authenticated_user()

    await delete_user(client, user['access_token'])

    response = await delete_user(client, user['access_token'])

    assert response.status_code == 403
    assert response.json()["detail"] == "account is deleted"


@pytest.mark.asyncio
async def test_delete_user_login_after_delete(client, authenticated_user):
    user = await authenticated_user()

    await delete_user(client, user['access_token'])

    response = await login_user(client)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'


# ---------- POST USERS/RESTORE ----------
@pytest.mark.asyncio
async def test_users_restore_success(client, db, authenticated_user):
    auth_user = await authenticated_user()

    await delete_user(client, auth_user['access_token'])

    response = await restore_user(client)

    assert response.status_code == 200

    result = await db.execute(
        select(UserBase)
        .where(UserBase.email == DEFAULT_USER["email"])
    )

    user = result.scalar_one_or_none()

    assert user.is_active is True


@pytest.mark.asyncio
async def test_users_restore_user_not_exist(client):
    response = await restore_user(client)

    assert response.status_code == 404
    assert response.json()['detail'] == 'User does not exist'


@pytest.mark.asyncio
async def test_users_restore_user_is_active(client, authenticated_user):
    await authenticated_user()

    response = await restore_user(client)

    assert response.status_code == 409
    assert response.json()['detail'] == 'account is already active'


@pytest.mark.asyncio
async def test_users_restore_wrong_password(client, authenticated_user):
    user = await authenticated_user()

    await delete_user(client, user['access_token'])

    response = await restore_user(client, password="wrong_password")

    assert response.status_code == 401
    assert response.json()["detail"] == "password is incorrect"


# ---------- GET USERS/{USER_ID} ----------
@pytest.mark.asyncio
async def test_get_users_userid_success(client, authenticated_user, thought_factory):
    user_1 = await authenticated_user()
    user_2 = await authenticated_user(email='test2@gmail.com', name='Test2')

    for text in ['1', '2']:
        await thought_factory(
            author_id=user_1['user'].id,
            text=text
        )

    response = await get_user(
        client, 
        user_2["access_token"],
        user_id=user_1["user"].id
    )

    assert response.status_code == 200

    data = response.json()

    assert data['name'] == DEFAULT_USER["name"]

    thoughts = data["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2

    assert thoughts["items"][0]["text"] == "1"
    assert thoughts["items"][1]["text"] == "2"


@pytest.mark.asyncio
async def test_get_users_userid_wrong_id(client, authenticated_user):
    user = await authenticated_user()

    response = await get_user(
        client,
        user['access_token'],
        user_id=9999
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'user not found'


@pytest.mark.asyncio
async def test_get_users_userid_private_account(client, authenticated_user):
    user_1 = await authenticated_user()
    user_2 = await authenticated_user(email='test2@gmail.com', name='Test2')

    await update_user(
        client,
        user_1['access_token'],
        is_private=True
    )

    response = await get_user(
        client, 
        user_2['access_token'],
        user_id=user_1['user'].id
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is private'


@pytest.mark.asyncio
async def test_get_users_userid_private_account_owner(client, authenticated_user):
    user = await authenticated_user()

    await update_user(
        client,
        user['access_token'],
        is_private=True
    )

    response = await get_user(
        client,
        user['access_token'],
        user_id=user['user'].id
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_users_userid_check_only_public_thoughts(client, authenticated_user, thought_factory):
    user_1 = await authenticated_user()
    user_2 = await authenticated_user(email='test2@gmail.com', name='Test2')

    for is_public in [False, True]:
        await thought_factory(
            author_id=user_1['user'].id,
            is_public=is_public
        )

    response = await get_user(
        client,
        user_2['access_token'],
        user_id=user_1['user'].id
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 1
    assert len(thoughts["items"]) == 1
    assert thoughts["items"][0]["is_public"] is True


@pytest.mark.asyncio
async def test_get_users_userid_public_private_owner(client, authenticated_user, thought_factory):
    user = await authenticated_user()

    for thought_is_public in [False, True]:
        await thought_factory(
            author_id=user['user'].id,
            is_public=thought_is_public
        )

    response = await get_user(
        client, 
        user['access_token'],
        user_id=user['user'].id
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2


@pytest.mark.asyncio
async def test_get_users_userid_user_without_thoughts(client, authenticated_user):
    user_1 = await authenticated_user()
    user_2 = await authenticated_user(email='test2@gmail.com', name='Test2')

    response = await get_user(
        client,
        user_2['access_token'],
        user_id=user_1['user'].id
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 0
    assert len(thoughts["items"]) == 0


@pytest.mark.asyncio
async def test_get_users_userid_search(client, authenticated_user, thought_factory):
    user_1 = await authenticated_user()
    user_2 = await authenticated_user(email='test2@gmail.com', name='Test2')

    for thought_text in ["search check", "SEARCH check", "TEST"]:
        await thought_factory(
            author_id=user_1['user'].id,
            text=thought_text
        )

    response = await get_user(
        client,
        user_2['access_token'],
        user_id=user_1['user'].id,
        search="search"
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 2
    assert len(thoughts["items"]) == 2

    assert thoughts["items"][0]["text"] == "search check"
    assert thoughts["items"][1]["text"] == "SEARCH check"


@pytest.mark.asyncio
async def test_get_users_userid_search_no_results(client, authenticated_user, thought_factory):
    user_1 = await authenticated_user()
    user_2 = await authenticated_user(email='test2@gmail.com', name='Test2')

    for thought_text in ["search check", "SEARCH check", "TEST"]:
        await thought_factory(
            author_id=user_1['user'].id,
            text=thought_text
        )

    response = await get_user(
        client,
        user_2['access_token'],
        user_id=user_1['user'].id,
        search="fortnite"
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 0
    assert len(thoughts["items"]) == 0


@pytest.mark.asyncio
async def test_get_users_userid_pagination(client, authenticated_user, thought_factory):
    user = await authenticated_user()

    created_thoughts = []

    for _ in range(5):
        thought_response = await thought_factory(
            author_id=user['user'].id
        )

        created_thoughts.append(thought_response)

    response = await get_user(
        client,
        user['access_token'],
        user_id=user['user'].id,
        limit=2,
        offset=2
    )

    assert response.status_code == 200

    thoughts = response.json()["thoughts"]

    assert thoughts["total"] == 5
    assert thoughts["items"][0]["id"] == created_thoughts[2].id
    assert thoughts["items"][1]["id"] == created_thoughts[3].id
    assert thoughts["has_next"] is True

