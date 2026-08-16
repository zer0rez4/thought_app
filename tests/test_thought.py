from tests.helpers.data import DEFAULT_USER, DEFAULT_THOUGHT

from tests.helpers.requests import (
    register_user,
    get_access_token,
    delete_user,
    auth_headers,
    create_thought,
    get_my_thoughts
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

    response = get_my_thoughts(client, access_token)

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

    response = get_my_thoughts(client, get_access_token(register_response))

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

    response = get_my_thoughts(client, access_token1)

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["author"] == "Test"


# ---------- GET THOUGHTS/{THOUGHT_ID} ----------
def test_get_thoughts_thoughtid_success(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='Test2@gmail.com')

    create_thought(client, get_access_token(register_response1))

    response = client.get(
        "/thoughts/1",
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data['id'], int)
    assert data['text'] == DEFAULT_THOUGHT['text']
    assert data['author'] == DEFAULT_USER['name']
    assert data['is_public'] is True


def test_get_thoughts_thoughtid_wrong_id(client):
    register_response = register_user(client)

    create_thought(client, get_access_token(register_response))

    response = client.get(
        "/thoughts/2",
        headers=auth_headers(get_access_token(register_response))
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'thought does not exist'


def test_get_thoughts_thoughtid_private_thought(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='Test2@gmail.com')

    create_thought(
        client, 
        get_access_token(register_response1),
        is_public=False
    )

    response = client.get(
        "/thoughts/1",
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'user has no rights'


def test_get_thoughts_thoughtid_private_thought_owner(client):
    register_response = register_user(client)

    create_thought(
        client, 
        get_access_token(register_response),
        is_public=False
    )

    response = client.get(
        "/thoughts/1",
        headers=auth_headers(get_access_token(register_response))
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data['id'], int)
    assert data['text'] == DEFAULT_THOUGHT['text']
    assert data['author'] == DEFAULT_USER['name']
    assert data['is_public'] is False


# ---------- GET THOUGHTS ----------
def test_get_thoughts_success(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='Test2@gmail.com')

    create_thought(
        client, 
        get_access_token(register_response1),
        text='1'
    )

    create_thought(
        client,
        get_access_token(register_response2),
        text='2'
    )

    response = client.get(
        '/thoughts',
        headers=auth_headers(get_access_token(register_response1))
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 2
    assert data['total'] == 2
    assert data['items'][0]['text'] == '1'
    assert data['items'][1]['text'] == '2'


def test_get_thoughts_no_public_thoughts(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='Test2@gmail.com')

    access_token1 = get_access_token(register_response1)

    create_thought(
        client, 
        access_token1,
        is_public=False
    )

    create_thought(
        client,
        access_token1,
        is_public=False
    )

    response = client.get(
        '/thoughts',
        headers=auth_headers(get_access_token(register_response2))
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 0
    assert data['total'] == 0


def test_get_thoughts_private_thoughts_owner(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(
        client, 
        access_token,
        is_public=False
    )

    create_thought(
        client,
        access_token,
        is_public=False
    )

    response = client.get(
        '/thoughts',
        headers=auth_headers(access_token)
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 2
    assert data['total'] == 2

    assert all(item["is_public"] is False for item in data["items"])


def test_get_thoughts_no_thoughts(client):
    register_response = register_user(client)

    response = client.get(
        '/thoughts',
        headers=auth_headers(get_access_token(register_response))
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 0
    assert data['total'] == 0


# ---------- PATCH THOUGHTS/{THOUGHT_ID} ----------
def test_patch_thought_change_text_success(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(client, access_token)

    response = client.patch(
        "/thoughts/1",
        json={
            "text": "New test text"
        },
        headers=auth_headers(access_token)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["text"] == "New test text"
    assert data["id"] == 1


def test_patch_thought_change_is_public_success(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(client, access_token)

    response = client.patch(
        "/thoughts/1",
        json={
            "is_public": False
        },
        headers=auth_headers(access_token)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_public"] == False
    assert data["id"] == 1


def test_patch_thought_empty_text(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(client, access_token)

    response = client.patch(
        "/thoughts/1",
        json={
            "text": "   "
        },
        headers=auth_headers(access_token)
    )

    assert response.status_code == 422

    data = response.json()

    assert 'Text can not be empty' in data['detail'][0]['msg']\


def test_patch_thought_another_user(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email="Test2@gmail.com")

    access_token1 = get_access_token(register_response1)
    access_token2 = get_access_token(register_response2)

    create_thought(client, access_token1)

    response = client.patch(
        "/thoughts/1",
        json={
            "text": "new_text"
        },
        headers=auth_headers(access_token2)
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "user has no rights"


def test_patch_thought_with_none_params(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(client, access_token)

    response = client.patch(
        "/thoughts/1",
        json={
            "text": None,
            "is_public": None
        },
        headers=auth_headers(access_token)
    )

    assert response.status_code == 200

    data = response.json()

    assert data['text'] == DEFAULT_THOUGHT["text"]
    assert data['is_public'] == DEFAULT_THOUGHT["is_public"]


# ---------- DELETE THOUGHTS/{THOUGHT_ID} ----------
def test_delete_thought_success(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(client, access_token)

    response = client.delete(
        "/thoughts/1",
        headers=auth_headers(access_token)
    )

    assert response.status_code == 204

    data = client.get(
        "/thoguhts/1"
    ).json()

    assert data['detail'] == 'Not Found'


def test_delete_thought_twice(client):
    register_response = register_user(client)

    access_token = get_access_token(register_response)

    create_thought(client, access_token)

    client.delete(
        "/thoughts/1",
        headers=auth_headers(access_token)
    )

    response = client.delete(
        "/thoughts/1",
        headers=auth_headers(access_token)
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'thought does not exist'


def test_delete_thought_another_user(client):
    register_response1 = register_user(client)
    register_response2 = register_user(client, email='Test2@gmail.com') 

    access_token1 = get_access_token(register_response1)
    access_token2 = get_access_token(register_response2)

    create_thought(client, access_token1)

    response = client.delete(
        "thoughts/1",
        headers=auth_headers(access_token2)
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'user has no rights'