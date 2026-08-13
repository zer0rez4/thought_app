from tests.helpers import (
    DEFAULT_USER,
    DEFAULT_THOUGHT,
    register_user,
    get_access_token,
    delete_user,

    create_thought,
    auth_headers
)

# ---------- POST THOUGHTS ----------
def test_post_thoughts_success(client):
    register_response = register_user(client)

    response = create_thought(
        client,
        get_access_token(register_response) 
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["text"] == DEFAULT_THOUGHT["text"]
    assert data["author"] == DEFAULT_USER["name"]
    assert data["is_public"] == DEFAULT_THOUGHT["is_public"]


def test_post_thoughts_with_none_text(client):
    register_response = register_user(client)

    response = create_thought(
        client,
        get_access_token(register_response),
        text=None
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert msg == 'Input should be a valid string'


def test_post_thoughts_with_none_is_public(client):
    register_response = register_user(client)

    response = create_thought(
        client,
        get_access_token(register_response),
        is_public=None
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert msg == 'Input should be a valid boolean'


def test_post_thoughts_with_space_text(client):
    register_response = register_user(client)

    response = create_thought(
        client,
        get_access_token(register_response),
        text="     "
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert 'Text can not be empty' in msg


# ---------- GET THOUGHTS/RANDOM ----------
def test_get_random_thought_success(client):
    register_response = register_user(client)

    for _ in range(5):
        create_thought(client, get_access_token(register_response))

    response = client.get(
        "/thoughts/random"    
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data['is_public'] is True


def test_get_random_thought_no_public_thoughts(client):
    register_response = register_user(client)

    for _ in range(5):
        create_thought(
            client, 
            get_access_token(register_response),
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


def test_get_random_thought_with_deleted_user(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(client, access_token)

    delete_user(client, access_token)

    response = client.get("/thoughts/random")

    assert response.status_code == 200

    data = response.json()

    assert data['author'] == 'deleted user'
    assert data["is_public"] is True


# ---------- GET THOUGHTS/MY ----------
def test_get_thoughts_my_success(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(
        client,
        access_token
    )

    create_thought(
        client,
        access_token,
        is_public=False
    )

    response = client.get(
        "/thoughts/my",
        headers=auth_headers(access_token)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    items = data["items"]

    assert len(items) == 2

    is_public_list = [items[0]["is_public"], items[1]["is_public"]]

    assert True in is_public_list
    assert False in is_public_list


def test_get_thoughts_my_without_thoughts(client):
    register_response = register_user(client)

    response = client.get(
        "/thoughts/my",
        headers=auth_headers(get_access_token(register_response))
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 0
    assert data["total"] == 0


def test_get_thoughts_my_no_other_thoughts(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email="TEST2@gmail.com", name="Test2")

    access_token1 = get_access_token(register_response1)
    access_token2 = get_access_token(register_response2)

    create_thought(client, access_token1)
    create_thought(client, access_token2)

    response = client.get(
        "/thoughts/my",
        headers=auth_headers(access_token1)
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["author"] == "Test"
