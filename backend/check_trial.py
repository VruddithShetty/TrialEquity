import asyncio
from database import init_db
from models import Trial, User
from bson import ObjectId

async def check_trial():
    await init_db()
    
    trial_id = "692c17de0a6dd5d78c09e2d1"
    
    try:
        trial = await Trial.get(ObjectId(trial_id))
        if trial:
            print(f"Trial found: {trial.filename}")
            print(f"Uploaded by ID: {trial.uploaded_by}")
            print(f"ML Status: {trial.ml_status}")
            print(f"Blockchain status: {trial.blockchain_status}")
            
            # Check if uploader exists
            if trial.uploaded_by:
                try:
                    uploader = await User.get(trial.uploaded_by)
                    if uploader:
                        print(f"Uploader exists: {uploader.username}")
                    else:
                        print(f"⚠️ Uploader NOT FOUND - User ID {trial.uploaded_by} doesn't exist!")
                except Exception as e:
                    print(f"⚠️ Error fetching uploader: {e}")
        else:
            print(f"Trial NOT FOUND")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_trial())
