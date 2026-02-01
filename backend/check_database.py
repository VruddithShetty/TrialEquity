"""
Diagnostic script to check database contents
"""
import asyncio
from database import init_db
from models import User, Trial

async def check_database():
    print("Initializing database connection...")
    await init_db()
    
    # Check users
    print("\n=== USERS IN DATABASE ===")
    users = await User.find_all().to_list()
    for user in users:
        print(f"Username: {user.username}, Email: {user.email}, Role: {user.role}, ID: {user.id}")
    
    # Check trials
    print("\n=== RECENT TRIALS (Last 15) ===")
    trials = await Trial.find_all().sort("-uploaded_at").limit(15).to_list()
    
    # Create user ID to username map
    user_map = {str(u.id): u.username for u in users}
    
    for trial in trials:
        uploaded_by_str = str(trial.uploaded_by) if trial.uploaded_by else "None"
        uploader_name = user_map.get(uploaded_by_str, f"Unknown (ID: {uploaded_by_str})")
        
        print(f"\nFile: {trial.filename}")
        print(f"  Uploaded by ID: {trial.uploaded_by}")
        print(f"  Resolved username: {uploader_name}")
        print(f"  Status: {trial.status}")
        print(f"  ML Status: {trial.ml_status}")
        print(f"  File path: {trial.file_path if trial.file_path else 'NOT SET'}")

if __name__ == "__main__":
    asyncio.run(check_database())
