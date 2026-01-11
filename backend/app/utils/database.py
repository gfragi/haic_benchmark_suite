import os
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "haic_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme123")
DB_NAME = os.getenv("DB_NAME", "haic_benchmark")

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# DATABASE_URL = "postgresql://haic_user:changeme123@localhost:5432/haic_benchmark" # Use for local development

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
# from app.models import *

# Base.metadata.create_all(bind=engine)
