from fastapi import FastAPI
from api.auth import router as auth_router
from api.thought import router as thought_router
from api.user import router as user_router

from database.models import Base
from database.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title='thoughts note')

app.include_router(auth_router)
app.include_router(thought_router)
app.include_router(user_router)

@app.get('/')
def test():
    return {'status':'ok'}

