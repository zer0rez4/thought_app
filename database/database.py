import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(dotenv_path='thought_app/.env')

db_url = os.getenv('SQLALCHEMY_DATABASE_URL')

engine = create_engine(
    db_url, connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
