DEFAULT_USER = {
    'email': 'test@gmail.com',
    'password': '12345678',
    'name': 'Test'
}

def register_user(client, **kwargs):
    data = DEFAULT_USER.copy()
    data.update(kwargs)

    if "name" in kwargs and kwargs["name"] is None:
        del data["name"]
    
    return client.post('/register', json=data)


def login_user(client, **kwargs):
    data = {
        "email": DEFAULT_USER["email"],
        "password": DEFAULT_USER["password"],
    }

    data.update(kwargs)

    return client.post("/login", json=data)


def assert_tokens(data):
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"


def refresh_user(client, refresh_token):
    return client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )
