from tests.helpers.data import DEFAULT_THOUGHT

from app.database.models import ThoughtBase


def create_thought_in_db(
    db,
    author_id,
    text=DEFAULT_THOUGHT["text"],
    is_public=DEFAULT_THOUGHT["is_public"]
):

    thought = ThoughtBase(
        author_id=author_id,
        text=text,
        is_public=is_public
    )

    db.add(thought)
    db.flush()

    return thought