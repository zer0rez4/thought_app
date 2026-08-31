from app.database.models import UserBase
from app.core.security import hash_password

from tests.helpers.data import DEFAULT_USER

def create_user_in_db(db, email=DEFAULT_USER["email"], password=DEFAULT_USER["password"], name=DEFAULT_USER["name"]):
    user = UserBase(
        email = email,
        hashed_password = hash_password(password),
        name = name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

