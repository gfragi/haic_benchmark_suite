import os
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL = os.getenv("DATABASE_URL") # Use for production

DATABASE_URL = "postgresql://postgres:CHANGEME123@localhost:5432/test_bench" # Use for local development

metadata = MetaData()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ensure all models are imported
from app.models import *

Base.metadata.create_all(bind=engine)
