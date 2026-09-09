from tests.helpers.data import DEFAULT_USER, DEFAULT_THOUGHT

from tests.helpers.requests import (
    delete_user,
    
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


def test_post_thoughts_with_none_text(client, authenticated_user):
    response = create_thought(
        client,
        authenticated_user()['access_token'],
        text=None
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert msg == 'Input should be a valid string'


def test_post_thoughts_with_none_is_public(client, authenticated_user):
    response = create_thought(
        client,
        authenticated_user()['access_token'],
        is_public=None
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert msg == 'Input should be a valid boolean'


def test_post_thoughts_with_space_text(client, authenticated_user):
    response = create_thought(
        client,
        authenticated_user()['access_token'],
        text="     "
    )

    assert response.status_code == 422

    msg = response.json()['detail'][0]['msg']

    assert 'Text can not be empty' in msg


# ---------- GET THOUGHTS/RANDOM ----------
def test_get_random_thought_success(client, thought_factory, authenticated_user):
    user = authenticated_user()

    for _ in range(5):
        thought_factory(
            author_id = user['user'].id
        )

    response = client.get(
        "/thoughts/random"    
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data['is_public'] is True


def test_get_random_thought_no_public_thoughts(client, thought_factory, authenticated_user):
    user = authenticated_user()

    for _ in range(5):
        thought_factory(
            author_id = user['user'].id,
            is_public = False
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


def test_get_random_thought_with_deleted_user(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought_factory(author_id = user['user'].id)

    delete_user(client, user['access_token'])

    response = client.get("/thoughts/random")

    assert response.status_code == 200

    data = response.json()

    assert data['author'] == 'deleted user'
    assert data["is_public"] is True


# ---------- GET THOUGHTS/MY ----------
def test_get_thoughts_my_success(client, authenticated_user, thought_factory):
    user = authenticated_user()

    for thought_is_public in [True, False]:
        thought_factory(
            author_id = user['user'].id,
            is_public=thought_is_public
        )

    response = get_my_thoughts(client, user['access_token'])

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    items = data["items"]

    assert len(items) == 2
    assert {item["is_public"] for item in items} == {True, False}


def test_get_thoughts_my_without_thoughts(client, authenticated_user):
    response = get_my_thoughts(client, authenticated_user()['access_token'])

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 0
    assert data["total"] == 0


def test_get_thoughts_my_no_other_thoughts(client, authenticated_user, thought_factory):
    user_1 = authenticated_user()
    user_2 = authenticated_user(email='test2@gmail.com', name='Test2')

    thought_factory(author_id = user_1['user'].id)
    thought_factory(author_id = user_2['user'].id)

    response = get_my_thoughts(client, user_1['access_token'])

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["author"] == "Test"


# ---------- GET THOUGHTS/{THOUGHT_ID} ----------
def test_get_thoughts_thoughtid_success(client, authenticated_user, thought_factory):
    user_1 = authenticated_user()
    user_2 = authenticated_user(email='test2@gmail.com', name='Test2')


    thought = thought_factory(
        author_id = user_1["user"].id
    )

    response = get_thought(
        client,
        user_2['access_token'],
        thought_id=thought.id
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data['id'], int)
    assert data['text'] == DEFAULT_THOUGHT['text']
    assert data['author'] == DEFAULT_USER['name']
    assert data['is_public'] is True


def test_get_thoughts_thoughtid_wrong_id(client, authenticated_user):
    response = get_thought(
        client,
        authenticated_user()['access_token'],
        thought_id=9999
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'thought does not exist'


def test_get_thoughts_thoughtid_private_thought(client, authenticated_user, thought_factory):
    user_1 = authenticated_user()
    user_2 = authenticated_user(email='test2@gmail.com', name='Test2')

    thought = thought_factory(
        author_id = user_1['user'].id,
        is_public = False
    )

    response = get_thought(
        client,
        user_2['access_token'],
        thought_id=thought.id
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'user has no rights'


def test_get_thoughts_thoughtid_private_thought_owner(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought = thought_factory(
        author_id = user['user'].id,
        is_public = False
    )

    response = get_thought(
        client,
        user['access_token'],
        thought_id=thought.id
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data['id'], int)
    assert data['text'] == DEFAULT_THOUGHT['text']
    assert data['author'] == DEFAULT_USER['name']
    assert data['is_public'] is False


# ---------- GET THOUGHTS ----------
def test_get_thoughts_success(client, authenticated_user, thought_factory):
    user_1 = authenticated_user()
    user_2 = authenticated_user(email='test2@gmail.com', name='Test2')


    thought_factory(
        author_id = user_1['user'].id,
        text = '1'
    )

    thought_factory(
        author_id = user_2['user'].id,
        text = '2'
    )

    response = get_thoughts(
        client,
        user_1['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 2
    assert data['total'] == 2
    assert data['items'][0]['text'] == '1'
    assert data['items'][1]['text'] == '2'


def test_get_thoughts_no_public_thoughts(client, authenticated_user, thought_factory):
    user_1 = authenticated_user()
    user_2 = authenticated_user(email='test2@gmail.com', name='Test2')

    for _ in range(3):
        thought_factory(
            author_id = user_1['user'].id,
            is_public = False
        )

    response = get_thoughts(
        client,
        user_2['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 0
    assert data['total'] == 0


def test_get_thoughts_private_thoughts_owner(client, authenticated_user, thought_factory):
    user = authenticated_user()

    for _ in range(3):
        thought_factory(
            author_id = user['user'].id,
            is_public = False
        )

    response = get_thoughts(
        client,
        user['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 3
    assert data['total'] == 3

    assert all(item["is_public"] is False for item in data["items"])


def test_get_thoughts_no_thoughts(client, authenticated_user):
    response = get_thoughts(
        client,
        authenticated_user()['access_token']
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 0
    assert data['total'] == 0


# ---------- PATCH THOUGHTS/{THOUGHT_ID} ----------
def test_patch_thought_change_text_success(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought = thought_factory(author_id = user['user'].id)

    response = update_thought(
        client,
        user['access_token'],
        thought_id=thought.id,
        text='New test text'
    )

    assert response.status_code == 200

    data = response.json()

    assert data["text"] == "New test text"
    assert data["id"] == thought.id


def test_patch_thought_change_is_public_success(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought = thought_factory(author_id = user['user'].id)

    response = update_thought(
        client,
        user['access_token'],
        thought_id=thought.id,
        is_public=False
    )

    assert response.status_code == 200

    data = response.json()

    assert data["is_public"] == False
    assert data["id"] == thought.id


def test_patch_thought_empty_text(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought = thought_factory(author_id = user['user'].id)

    response = update_thought(
        client,
        user['access_token'],
        thought_id=thought.id,
        text="     "
    )

    assert response.status_code == 422

    data = response.json()

    assert 'Text can not be empty' in data['detail'][0]['msg']


def test_patch_thought_another_user(client, authenticated_user, thought_factory):
    user_1 = authenticated_user()
    user_2 = authenticated_user(email='test2@gmail.com', name='Test2')

    thought = thought_factory(author_id = user_1['user'].id)

    response = update_thought(
        client,
        user_2['access_token'],
        thought_id=thought.id,
        text='New test text'
    )

    assert response.status_code == 403
    assert response.json()['detail'] == "user has no rights"


def test_patch_thought_with_none_params(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought = thought_factory(author_id = user['user'].id)

    response = update_thought(
        client,
        user['access_token'],
        thought_id=thought.id,
        text=None,
        is_public=None
    )

    assert response.status_code == 200

    data = response.json()

    assert data['text'] == DEFAULT_THOUGHT["text"]
    assert data['is_public'] == DEFAULT_THOUGHT["is_public"]


# ---------- DELETE THOUGHTS/{THOUGHT_ID} ----------
def test_delete_thought_success(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought = thought_factory(author_id = user['user'].id)

    response = delete_thought(
        client,
        user['access_token'],
        thought_id=thought.id
    )

    assert response.status_code == 204

    data = get_thought(
        client,
        user['access_token'],
        thought_id=thought.id
    ).json()

    assert data['detail'] == 'thought does not exist'


def test_delete_thought_twice(client, authenticated_user, thought_factory):
    user = authenticated_user()

    thought = thought_factory(author_id = user['user'].id)

    delete_thought(
        client,
        user['access_token'],
        thought_id=thought.id
    )

    response = delete_thought(
        client,
        user['access_token'],
        thought_id=thought.id
    )

    assert response.status_code == 404
    assert response.json()['detail'] == 'thought does not exist'


def test_delete_thought_another_user(client, authenticated_user, thought_factory):
    user_1 = authenticated_user()
    user_2 = authenticated_user(email='test2@gmail.com', name='Test2')

    thought = thought_factory(author_id = user_1['user'].id)

    response = delete_thought(
        client,
        user_2['access_token'],
        thought_id=thought.id
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'user has no rights'