from sqlalchemy import select

from app.database.models import RefreshTokenBase
from tests.helpers.data import DEFAULT_USER, DEFAULT_THOUGHT


# ---------- DEFAULT ----------
async def register_user(client, **kwargs):
    data = DEFAULT_USER.copy()
    data.update(kwargs)

    if "name" in kwargs and kwargs["name"] is None:
        del data["name"]
    
    return await client.post('/register', json=data)


async def login_user(client, **kwargs):
    data = {
        "email": DEFAULT_USER["email"],
        "password": DEFAULT_USER["password"],
    }

    data.update(kwargs)

    return await client.post("/login", json=data)


def get_refresh_token(response):
    return response.json()['refresh_token']


def get_access_token(response):
    return response.json()['access_token']


def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


# ---------- AUTH ----------
async def refresh_user(client, refresh_token):
    return await client.post(
        "/refresh",
        json={
            "refresh_token": refresh_token
        }
    )


async def logout_user(client, refresh_token):
    return await client.post(
        "/logout",
        json={
            "refresh_token": refresh_token
        }
    )


async def delete_refresh_token_from_db(db, token):
    result = await db.execute(
        select(RefreshTokenBase)
        .where(RefreshTokenBase.token == token)
    )

    refresh = result.scalar_one_or_none()


    await db.delete(refresh)
    await db.commit()


# ---------- USERS ----------
async def get_users_me(client, access_token):
    return await client.get(
        "/users/me",
        headers=auth_headers(access_token)
    )


async def update_user(client, access_token=None, new_name=None, is_private=None):
    headers = auth_headers(access_token) if access_token else None

    return await client.patch(
        "/users/me",
        json={
            "new_name": new_name,
            "is_private": is_private
        },
        headers=headers
    )


async def delete_user(client, access_token):
    return await client.delete(
        "/users/me",
        headers=auth_headers(access_token)
    )


async def restore_user(client, **kwargs):
    data = {
        "email": DEFAULT_USER["email"],
        "password": DEFAULT_USER["password"],
    }

    data.update(kwargs)

    return await client.post(
        "/users/restore",
        json=data
    )


async def get_user(client, access_token, user_id, **kwargs):
    return await client.get(
        f"/users/{user_id}",
        params=kwargs,
        headers=auth_headers(access_token)
    )


# ---------- THOUGHTS ----------
async def create_thought(client, access_token, text=DEFAULT_THOUGHT["text"], is_public=DEFAULT_THOUGHT["is_public"]):
    return await client.post(
        "/thoughts",
        json={
            "text": text,
            "is_public": is_public
        },
        headers=auth_headers(access_token)
    )


async def get_my_thoughts(client, access_token, **kwargs):
    return await client.get(
        "/thoughts/my",
        headers=auth_headers(access_token),
        params=kwargs
    )


async def get_thought(client, access_token, thought_id, **kwargs):
    return await client.get(
        f"/thoughts/{thought_id}",
        params=kwargs,
        headers=auth_headers(access_token)
    )


async def get_thoughts(client, access_token, **kwargs):
    return await client.get(
        "/thoughts",
        params=kwargs,
        headers=auth_headers(access_token)
    )


async def update_thought(client, access_token, thought_id, text=None, is_public=None):
    headers = auth_headers(access_token) if access_token else None

    return await client.patch(
        f"/thoughts/{thought_id}",
        json={
            "text": text,
            "is_public": is_public
        },
        headers=headers
    )


async def delete_thought(client, access_token, thought_id):
    return await client.delete(
        f"/thoughts/{thought_id}",
        headers=auth_headers(access_token)
    )