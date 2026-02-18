import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling configuration
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Turn off verbose logging
    pool_pre_ping=True,  # Test connections before using
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum overflow connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
)

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session

def create_tables():
    """Create all tables in the database"""
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database connection warning: {e}")
        print("   This is okay if database tables already exist")
