# ---------- REGISTER ----------

def test_register_success(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678",
        "name": "Test"
    }

    response = client.post('/register', json=user_data)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"


def test_register_existing_email(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678",
        "name": "Test"
    }

    client.post('/register', json=user_data)
    response = client.post('/register', json=user_data)

    assert response.status_code == 400
    assert response.json()['detail'] == "User already exists"


def test_register_invalid_email(client):
    user_data = {
        "email": "just_email",
        "password": "12345678",
        "name": "Test"
    }

    response = client.post('/register', json=user_data)

    assert response.status_code == 422


def test_register_short_password(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "1",
        "name": "Test"
    }

    response = client.post('/register', json=user_data)

    assert response.status_code == 422


def test_register_invalid_name(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678",
        "name": " "
    }

    response = client.post('/register', json=user_data)

    assert response.status_code == 422


def test_register_without_name(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678"
    }

    response = client.post('/register', json=user_data)

    assert response.status_code == 422


# ---------- LOGIN ----------

def test_login_success(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678",
        "name": "Test"
    }

    client.post('/register', json=user_data)

    login_data = {
        "email": "test@gmail.com",
        "password": "12345678"
    }

    response = client.post('/login', json=login_data)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"


#Юзер удален (is_active = False)


def test_login_wrong_password(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678",
        "name": "Test"
    }

    client.post('/register', json=user_data)

    login_data = {
        "email": "test@gmail.com",
        "password": "87654321",
    }

    response = client.post('/login', json=login_data)

    assert response.status_code == 401
    assert response.json()['detail'] == 'password is incorrect'


def test_login_unknown_user(client):
    login_data = {
        "email": "test@gmail.com",
        "password": "12345678",
    }

    response = client.post('/login', json=login_data)

    assert response.status_code == 404
    assert response.json()['detail'] == 'User does not exist'


def test_login_deleted_user(client):
    user_data = {
        "email": "test@gmail.com",
        "password": "12345678",
        "name": "Test"
    }

    register_response = client.post('/register', json=user_data)
    
    access_token = register_response.json()['access_token']
    
    client.delete(
        '/users/me', 
        headers={
            "Authorization": f"Bearer {access_token}"
            }
        )


    login_data = {
        "email": "test@gmail.com",
        "password": "12345678",
    }

    response = client.post('/login', json=login_data)

    assert response.status_code == 403
    assert response.json()['detail'] == 'account is deleted'
