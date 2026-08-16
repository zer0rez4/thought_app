from app.database.models import RefreshTokenBase
from tests.helpers.data import DEFAULT_USER, DEFAULT_THOUGHT


# ---------- DEFAULT ----------
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


def delete_refresh_token_from_db(db, token):
    refresh = (
        db.query(RefreshTokenBase)
        .filter(RefreshTokenBase.token == token)
        .first()
    )

    db.delete(refresh)
    db.commit()


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
def create_thought(client, access_token, text=DEFAULT_THOUGHT["text"], is_public=DEFAULT_THOUGHT["is_public"]):
    return client.post(
        "/thoughts",
        json={
            "text": text,
            "is_public": is_public
        },
        headers=auth_headers(access_token)
    )


def get_my_thoughts(client, access_token, **kwargs):
    return client.get(
        "/thoughts/my",
        headers=auth_headers(access_token),
        params=kwargs
    )