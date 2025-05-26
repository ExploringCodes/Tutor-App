from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# You can use environment variables or hardcode this (not recommended)
#DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:iamgreat@localhost:5432/AITutor")

DATABASE_URL = "postgresql://postgres:abcd1234@localhost/AITutor"
#DATABASE_URL = "postgresql://postgres:DEz(*5uf5\PaGGjl@34.47.195.36/AITutor"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
