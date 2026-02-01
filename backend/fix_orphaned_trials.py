"""
Fix orphaned trials that reference deleted users
"""
import asyncio
from database import init_db
from models import Trial, User
from bson import ObjectId

async def fix_orphaned_trials():
    await init_db()
    
    print("\n=== CHECKING FOR ORPHANED TRIALS ===\n")
    
    # Get all trials
    trials = await Trial.find_all().to_list()
    print(f"Total trials: {len(trials)}")
    
    # Get all user IDs
    users = await User.find_all().to_list()
    user_ids = {str(u.id) for u in users}
    print(f"Total users: {len(users)}")
    
    # Find orphaned trials
    orphaned = []
    for trial in trials:
        if trial.uploaded_by and str(trial.uploaded_by) not in user_ids:
            orphaned.append(trial)
    
    if not orphaned:
        print("\n✅ No orphaned trials found!")
        return
    
    print(f"\n⚠️ Found {len(orphaned)} orphaned trials:\n")
    
    for trial in orphaned:
        print(f"  - {trial.filename} (ID: {trial.id})")
        print(f"    References deleted user: {trial.uploaded_by}")
        print(f"    ML Status: {trial.ml_status}")
        print(f"    Blockchain Status: {trial.blockchain_status or 'None'}\n")
    
    # Ask for action
    print("\nOptions:")
    print("1. Delete all orphaned trials")
    print("2. Reassign to admin user")
    print("3. Cancel")
    
    choice = input("\nChoose option (1/2/3): ")
    
    if choice == "1":
        print("\n⚠️ Deleting orphaned trials...")
        for trial in orphaned:
            print(f"  Deleting: {trial.filename}")
            await trial.delete()
        print(f"\n✅ Deleted {len(orphaned)} orphaned trials")
        
    elif choice == "2":
        # Find admin user
        admin = await User.find_one(User.role == "ADMIN")
        if not admin:
            print("❌ No admin user found!")
            return
        
        print(f"\n✅ Reassigning to admin: {admin.username} (ID: {admin.id})")
        for trial in orphaned:
            print(f"  Reassigning: {trial.filename}")
            trial.uploaded_by = admin.id
            await trial.save()
        print(f"\n✅ Reassigned {len(orphaned)} trials to admin")
        
    else:
        print("\nCancelled")

if __name__ == "__main__":
    asyncio.run(fix_orphaned_trials())
