from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.thought import router as thought_router
from app.api.user import router as user_router

from app.database.models import Base
from app.database.database import engine

app = FastAPI(title='thoughts note')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(thought_router)
app.include_router(user_router)

@app.get('/')
def test():
    return {'status':'ok'}

