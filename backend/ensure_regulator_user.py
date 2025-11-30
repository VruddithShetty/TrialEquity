"""
Ensure REGULATOR user exists for testing
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db
from models import User
from auth import get_password_hash

async def ensure_regulator_user():
    await init_db()
    
    # Check if regulator user exists
    regulator = await User.find_one(User.email == "regulator@example.com")
    
    if not regulator:
        regulator_user = User(
            email="regulator@example.com",
            username="regulator",
            hashed_password=get_password_hash("test123"),
            role="REGULATOR",
            organization="FDA Regulatory"
        )
        await regulator_user.insert()
        print("✅ Created REGULATOR user: regulator@example.com / test123")
    else:
        print("✅ REGULATOR user already exists")
    
    # Also ensure SPONSOR user exists
    sponsor = await User.find_one(User.email == "test@example.com")
    if not sponsor:
        sponsor_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("test123"),
            role="SPONSOR",
            organization="Test Organization"
        )
        await sponsor_user.insert()
        print("✅ Created SPONSOR user: test@example.com / test123")
    else:
        print("✅ SPONSOR user already exists")

if __name__ == "__main__":
    asyncio.run(ensure_regulator_user())

