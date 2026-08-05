# ---------- SERVICES ----------
def register_user(
        client,
        email="test@gmail.com",
        password="12345678",
        name="Test"
):
    
    return client.post(
        '/register', 
        json={
            "email": email,
            "password": password,
            "name": name
        }
    )


def login_user(
    client,
    email="test@gmail.com",
    password="12345678",
):
    return client.post(
        "/login",
        json={
            "email": email,
            "password": password,
        },
    )


# ---------- REGISTER ----------

def test_register_success(client):
    response = register_user(client)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"


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

# вопрос как удалить из хелпер функции, передать None?
def test_register_without_name(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678"
    }

    response = client.post('/register', json=user_data)

    assert response.status_code == 422


# ---------- LOGIN ----------

def test_login_success(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"


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
