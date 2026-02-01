#!/usr/bin/env python3
"""
Secure Admin Account Setup Script
Run this script ONCE when setting up the system for the first time.
This creates the initial admin account without hardcoding credentials.
"""

import asyncio
import sys
import getpass
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, close_db
from models import User
from auth import get_password_hash


async def setup_admin():
    """Create initial admin account"""
    
    print("=" * 60)
    print("  CLINICAL TRIAL PLATFORM - ADMIN ACCOUNT SETUP")
    print("=" * 60)
    print()
    
    # Initialize database
    await init_db()
    
    # Check if any admin exists
    admin_count = await User.find(User.role == "ADMIN").count()
    if admin_count > 0:
        print("❌ ERROR: Admin account(s) already exist in the database!")
        print("   To reset, please delete the admin user(s) manually from MongoDB.")
        await close_db()
        return False
    
    print("Welcome! Let's create your initial admin account.")
    print()
    
    # Get email
    while True:
        email = input("Enter admin email: ").strip()
        if not email or "@" not in email:
            print("❌ Invalid email format. Please try again.")
            continue
        
        # Check if email already exists
        existing = await User.find_one(User.email == email)
        if existing:
            print("❌ This email is already registered!")
            continue
        break
    
    # Get username
    while True:
        username = input("Enter admin username: ").strip()
        if not username or len(username) < 3:
            print("❌ Username must be at least 3 characters.")
            continue
        
        # Check if username already exists
        existing = await User.find_one(User.username == username)
        if existing:
            print("❌ This username is already taken!")
            continue
        break
    
    # Get organization
    organization = input("Enter organization name (optional): ").strip() or "System Administration"
    
    # Get password
    print("\nPassword requirements:")
    print("  - Minimum 12 characters")
    print("  - Mix of uppercase, lowercase, numbers, and special characters")
    print()
    
    while True:
        password = getpass.getpass("Enter admin password: ")
        
        # Validate password strength
        if len(password) < 12:
            print("❌ Password must be at least 12 characters.")
            continue
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            print("❌ Password must contain uppercase, lowercase, numbers, and special characters.")
            continue
        
        # Confirm password
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("❌ Passwords do not match. Try again.")
            continue
        
        break
    
    # Create admin user
    print("\n🔄 Creating admin account...")
    
    try:
        admin_user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            role="ADMIN",
            organization=organization,
            is_active=True
        )
        await admin_user.insert()
        
        print("\n✅ SUCCESS! Admin account created.")
        print()
        print("=" * 60)
        print("  LOGIN CREDENTIALS")
        print("=" * 60)
        print(f"Email:    {email}")
        print(f"Username: {username}")
        print(f"Role:     ADMIN")
        print()
        print("⚠️  SECURITY REMINDER:")
        print("  - Store these credentials securely")
        print("  - Never share your password")
        print("  - Change your password after first login")
        print("=" * 60)
        print()
        
        await close_db()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Failed to create admin account: {e}")
        await close_db()
        return False


if __name__ == "__main__":
    success = asyncio.run(setup_admin())
    sys.exit(0 if success else 1)
