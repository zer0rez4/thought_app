from fastapi import FastAPI
from api.auth import router as auth_router
from api.thought import router as thought_router

app = FastAPI(title='thoughts note')

app.include_router(auth_router)
app.include_router(thought_router)

from api.auth import user_db_by_id

@app.get('/')
def test():
    return user_db_by_id
