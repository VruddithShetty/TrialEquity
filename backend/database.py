"""
MongoDB database configuration using Beanie ODM
"""
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    # Try loading with dotenv first
    load_dotenv(dotenv_path=env_path, override=True)
    
    # If still not loaded, manually parse the file
    if not os.getenv("MONGODB_URL") or os.getenv("MONGODB_URL") == "mongodb://localhost:27017":
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except Exception as e:
            print(f"⚠️  Error reading .env file: {e}")
else:
    # Try loading from current directory
    load_dotenv(override=True)

# MongoDB connection URL
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "clinical_trials")

# Debug: Print connection info (without password)
if MONGODB_URL and MONGODB_URL != "mongodb://localhost:27017":
    print(f"📡 Using MongoDB Atlas connection")
else:
    print(f"⚠️  Warning: Using default localhost connection. Check .env file!")
    print(f"   Looking for .env at: {env_path}")

# Global client
client: AsyncIOMotorClient = None

async def init_db():
    """Initialize MongoDB connection and Beanie"""
    global client
    
    # Create Motor client
    client = AsyncIOMotorClient(MONGODB_URL)
    
    # Initialize Beanie with document models
    from models import User, Trial, AuditLog
    
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[User, Trial, AuditLog]
    )
    
    print(f"✅ Connected to MongoDB: {DATABASE_NAME}")

async def close_db():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")

def get_db():
    """Dependency for getting database (for compatibility)"""
    # With Beanie, we don't need a session like SQLAlchemy
    # Documents are accessed directly
    return client[DATABASE_NAME]
