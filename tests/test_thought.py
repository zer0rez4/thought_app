from tests.helpers.data import DEFAULT_USER, DEFAULT_THOUGHT

from tests.helpers.requests import (
    register_user,
    get_access_token,
    delete_user,
    auth_headers,
    create_thought,
    get_my_thoughts,
    get_thought,
    get_thoughts,
    update_thought,
    delete_thought
)

# ---------- POST THOUGHTS ----------
def test_post_thoughts_success(created_thought_response):
    assert created_thought_response.status_code == 200

    data = created_thought_response.json()

    assert isinstance(data["id"], int)
    assert data["text"] == DEFAULT_THOUGHT["text"]
    assert data["author"] == DEFAULT_USER["name"]
    assert data["is_public"] == DEFAULT_THOUGHT["is_public"]


def test_post_thoughts_with_none_text(client, registered_user):
    response = create_thought(
        client,
        registered_user['access_token'],
        text=None
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert msg == 'Input should be a valid string'


def test_post_thoughts_with_none_is_public(client, registered_user):
    response = create_thought(
        client,
        registered_user['access_token'],
        is_public=None
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert msg == 'Input should be a valid boolean'


def test_post_thoughts_with_space_text(client, registered_user):
    response = create_thought(
        client,
        registered_user['access_token'],
        text="     "
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert 'Text can not be empty' in msg


# ---------- GET THOUGHTS/RANDOM ----------
def test_get_random_thought_success(client, registered_user):
    for _ in range(5):
        create_thought(client, registered_user['access_token'])

    response = client.get(
        "/thoughts/random"    
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data['is_public'] is True


def test_get_random_thought_no_public_thoughts(client, registered_user):
    for _ in range(5):
        create_thought(
            client, 
            registered_user['access_token'],
            is_public=False
        )

    response = client.get(
        "/thoughts/random"    
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == 'No available public thoughts'


def test_get_random_thought_with_no_thoughts(client):
    response = client.get(
        "/thoughts/random"    
    )

    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == 'No available public thoughts'


def test_get_random_thought_with_deleted_user(client, registered_user):
    create_thought(client, registered_user['access_token'])

    delete_user(client, registered_user['access_token'])

    response = client.get("/thoughts/random")

    assert response.status_code == 200

    data = response.json()

    assert data['author'] == 'deleted user'
    assert data["is_public"] is True


# ---------- GET THOUGHTS/MY ----------
def test_get_thoughts_my_success(client, registered_user):
    create_thought(
        client,
        registered_user['access_token']
    )

    create_thought(
        client,
        registered_user['access_token'],
        is_public=False
    )

    response = get_my_thoughts(client, registered_user['access_token'])

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    items = data["items"]

    assert len(items) == 2
    assert {item["is_public"] for item in items} == {True, False}


def test_get_thoughts_my_without_thoughts(client, registered_user):
    response = get_my_thoughts(client, registered_user['access_token'])

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 0
    assert data["total"] == 0


def test_get_thoughts_my_no_other_thoughts(client, created_two_users):
    create_thought(client, created_two_users['first']['access_token'])
    create_thought(client, created_two_users['second']['access_token'])

    response = get_my_thoughts(client, created_two_users['first']['access_token'])

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["author"] == "Test"


# ---------- GET THOUGHTS/{THOUGHT_ID} ----------
def test_get_thoughts_thoughtid_success(client, created_two_users):
    thought_response = create_thought(client, created_two_users['first']['access_token'])

    response = get_thought(
        client,
        created_two_users['second']['access_token'],
        thought_id=thought_response.json()['id']
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data['id'], int)
    assert data['text'] == DEFAULT_THOUGHT['text']
    assert data['author'] == DEFAULT_USER['name']
    assert data['is_public'] is True


def test_get_thoughts_thoughtid_wrong_id(client, registered_user):
    response = get_thought(
        client,
        registered_user['access_token'],
        thought_id=9999
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'thought does not exist'


def test_get_thoughts_thoughtid_private_thought(client, created_two_users):
    thought_response = create_thought(
        client, 
        created_two_users['first']['access_token'],
        is_public=False
    )

    response = get_thought(
        client,
        created_two_users['second']['access_token'],
        thought_id=thought_response.json()['id']
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'user has no rights'


def test_get_thoughts_thoughtid_private_thought_owner(client, registered_user):
    thought_response = create_thought(
        client, 
        registered_user['access_token'],
        is_public=False
    )

    response = get_thought(
        client,
        registered_user['access_token'],
        thought_id=thought_response.json()['id']
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data['id'], int)
    assert data['text'] == DEFAULT_THOUGHT['text']
    assert data['author'] == DEFAULT_USER['name']
    assert data['is_public'] is False


# ---------- GET THOUGHTS ----------
def test_get_thoughts_success(client, created_two_users):
    create_thought(
        client, 
        created_two_users['first']['access_token'],
        text='1'
    )

    create_thought(
        client,
        created_two_users['second']['access_token'],
        text='2'
    )

    response = get_thoughts(
        client,
        created_two_users['first']['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 2
    assert data['total'] == 2
    assert data['items'][0]['text'] == '1'
    assert data['items'][1]['text'] == '2'


def test_get_thoughts_no_public_thoughts(client, created_two_users):
    create_thought(
        client, 
        created_two_users['first']['access_token'],
        is_public=False
    )

    create_thought(
        client,
        created_two_users['first']['access_token'],
        is_public=False
    )

    response = get_thoughts(
        client,
        created_two_users['second']['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 0
    assert data['total'] == 0


def test_get_thoughts_private_thoughts_owner(client, registered_user):
    create_thought(
        client, 
        registered_user['access_token'],
        is_public=False
    )

    create_thought(
        client,
        registered_user['access_token'],
        is_public=False
    )

    response = get_thoughts(
        client,
        registered_user['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 2
    assert data['total'] == 2

    assert all(item["is_public"] is False for item in data["items"])


def test_get_thoughts_no_thoughts(client, registered_user):
    response = get_thoughts(
        client,
        registered_user['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 0
    assert data['total'] == 0


# ---------- PATCH THOUGHTS/{THOUGHT_ID} ----------
def test_patch_thought_change_text_success(client, registered_user, created_thought_response):
    response = update_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id'],
        text='New test text'
    )

    assert response.status_code == 200

    data = response.json()

    assert data["text"] == "New test text"
    assert data["id"] == created_thought_response.json()["id"]


def test_patch_thought_change_is_public_success(client, registered_user, created_thought_response):
    response = update_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id'],
        is_public=False
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_public"] == False
    assert data["id"] == created_thought_response.json()["id"]


def test_patch_thought_empty_text(client, registered_user, created_thought_response):
    response = update_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id'],
        text="     "
    )

    assert response.status_code == 422

    data = response.json()

    assert 'Text can not be empty' in data['detail'][0]['msg']\


def test_patch_thought_another_user(client, created_two_users):
    thought_response = create_thought(client, created_two_users['first']['access_token'])

    response = update_thought(
        client,
        created_two_users['second']['access_token'],
        thought_id=thought_response.json()['id'],
        text='New test text'
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "user has no rights"


def test_patch_thought_with_none_params(client, registered_user, created_thought_response):
    response = update_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id'],
        text=None,
        is_public=None
    )

    assert response.status_code == 200

    data = response.json()

    assert data['text'] == DEFAULT_THOUGHT["text"]
    assert data['is_public'] == DEFAULT_THOUGHT["is_public"]


# ---------- DELETE THOUGHTS/{THOUGHT_ID} ----------
def test_delete_thought_success(client, registered_user, created_thought_response):
    response = delete_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id']
    )

    assert response.status_code == 204

    data = get_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id']
    ).json()

    assert data['detail'] == 'thought does not exist'


def test_delete_thought_twice(client, registered_user, created_thought_response):
    delete_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id']
    )

    response = delete_thought(
        client,
        registered_user['access_token'],
        thought_id=created_thought_response.json()['id']
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'thought does not exist'


def test_delete_thought_another_user(client, created_two_users):
    thought_response = create_thought(client, created_two_users['first']['access_token'])

    response = delete_thought(
        client,
        created_two_users['second']['access_token'],
        thought_id=thought_response.json()['id']
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'user has no rights'