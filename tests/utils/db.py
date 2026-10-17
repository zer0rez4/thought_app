from sqlalchemy import select

from app.services.email_token import hash_email_token

from app.database.models import RefreshTokenBase, EmailTokenBase


async def delete_refresh_token_from_db(db, token):
    result = await db.execute(
        select(RefreshTokenBase)
        .where(RefreshTokenBase.token == token)
    )

    refresh = result.scalar_one_or_none()


    await db.delete(refresh)
    await db.commit()


async def get_email_token_from_db(db, token):
    result = await db.execute(
        select(EmailTokenBase).where(
            EmailTokenBase.token_hash == hash_email_token(token)
        )
    )

    token_from_db = result.scalar_one()

    return token_from_db


async def delete_email_token_from_db(db, token):
    result = await db.execute(
        select(EmailTokenBase)
        .where(EmailTokenBase.token_hash == hash_email_token(token))
    )

    email_token = result.scalar_one_or_none()

    await db.delete(email_token)
    await db.flush()
