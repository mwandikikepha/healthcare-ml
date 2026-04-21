import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # Load environment variables from .env file  

# 1. Define the Connection String
# Format: postgresql://user:password@host:port/dbname
DATABASE_URL = os.getenv("db_conn")

# 2. Create the Engine
# 'pool_pre_ping' checks if the connection is alive before using it
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 3. Create a Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class for our Models (used in database/models.py)
Base = declarative_base()

def get_engine():
    """Returns the sqlalchemy engine."""
    return engine

def get_db():
    """Dependency for FastAPI routes to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()