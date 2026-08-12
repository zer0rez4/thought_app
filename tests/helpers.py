from app.database.models import RefreshTokenBase

# ---------- DEFAULT ----------
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


def get_refresh_token(response):
    return response.json()['refresh_token']


def get_access_token(response):
    return response.json()['access_token']


def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


# ---------- AUTH ----------
def refresh_user(client, refresh_token):
    return client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )


def logout_user(client, refresh_token):
    return client.post(
        "/logout",
        json={
            "refresh_token": refresh_token
        }
    )


def delete_refresh_token(db, token):
    refresh = (
        db.query(RefreshTokenBase)
        .filter(RefreshTokenBase.token == token)
        .first()
    )

    db.delete(refresh)
    db.commit()


def assert_tokens(data):
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["access_token"] != ""
    assert data["refresh_token"] != ""
    assert data["token_type"] == "bearer"


# ---------- USERS ----------
def get_users_me(client, access_token):
    return client.get(
        "/users/me",
        headers=auth_headers(access_token)
    )


def update_user(client, access_token=None, new_name=None, is_private=None):
    headers = auth_headers(access_token) if access_token else None

    return client.patch(
        "/users/me",
        json={
            "new_name": new_name,
            "is_private": is_private
        },
        headers=headers
    )


def delete_user(client, access_token):
    return client.delete(
        "/users/me",
        headers=auth_headers(access_token)
    )


def restore_user(client, **kwargs):
    data = {
        "email": DEFAULT_USER["email"],
        "password": DEFAULT_USER["password"],
    }

    data.update(kwargs)

    return client.post(
        "/users/restore",
        json=data
    )


# ---------- THOUGHTS ----------
def create_thought(client, access_token, text="TEST TEXT", is_public=True):
    return client.post(
        "/thoughts",
        json={
            "text": text,
            "is_public": is_public
        },
        headers=auth_headers(access_token)
    )