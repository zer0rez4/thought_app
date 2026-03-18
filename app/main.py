from fastapi import FastAPI
from api.auth import router as auth_router

app = FastAPI(title='thoughts note')

app.include_router(auth_router)

@app.get('/')
def test():
    return {'status': 'ok'}
