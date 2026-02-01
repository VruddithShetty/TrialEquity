"""
Script to fix duplicate users in the database
"""
import asyncio
from database import init_db
from models import User

async def fix_duplicates():
    await init_db()
    
    print("\n=== CURRENT USERS ===")
    users = await User.find_all().to_list()
    
    # Group by username
    username_groups = {}
    for user in users:
        if user.username not in username_groups:
            username_groups[user.username] = []
        username_groups[user.username].append(user)
    
    # Show duplicates
    for username, user_list in username_groups.items():
        print(f"\nUsername: {username} - {len(user_list)} account(s)")
        for user in user_list:
            print(f"  ID: {user.id}, Email: {user.email}, Role: {user.role}")
        
        # If duplicates exist, keep the newest one
        if len(user_list) > 1:
            print(f"  ⚠️ DUPLICATE FOUND! Keeping newest, will delete others")
            # Sort by ID (newer IDs are larger in MongoDB)
            sorted_users = sorted(user_list, key=lambda u: str(u.id), reverse=True)
            keep = sorted_users[0]
            delete = sorted_users[1:]
            
            print(f"  ✅ KEEPING: ID={keep.id}, Email={keep.email}")
            for d in delete:
                print(f"  ❌ WILL DELETE: ID={d.id}, Email={d.email}")
    
    print("\n\n=== CLEANUP ACTIONS ===")
    response = input("Do you want to delete duplicate users? (yes/no): ")
    
    if response.lower() == 'yes':
        for username, user_list in username_groups.items():
            if len(user_list) > 1:
                sorted_users = sorted(user_list, key=lambda u: str(u.id), reverse=True)
                delete = sorted_users[1:]
                
                for d in delete:
                    print(f"Deleting user: {d.username} (ID={d.id})...")
                    await d.delete()
                    print(f"  ✅ Deleted")
        
        print("\n✅ Cleanup complete!")
        
        # Show remaining users
        print("\n=== REMAINING USERS ===")
        users = await User.find_all().to_list()
        for user in users:
            print(f"Username: {user.username}, Email: {user.email}, Role: {user.role}, ID: {user.id}")
    else:
        print("Cleanup cancelled")

if __name__ == "__main__":
    asyncio.run(fix_duplicates())
