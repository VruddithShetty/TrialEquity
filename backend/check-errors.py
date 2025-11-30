#!/usr/bin/env python3
"""
Diagnostic script to check for backend errors
"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("Backend Error Diagnostic Tool")
print("=" * 60)
print()

errors = []
warnings = []

# 1. Check Python version
print("1. Checking Python version...")
if sys.version_info < (3, 8):
    errors.append(f"Python 3.8+ required, found {sys.version}")
    print(f"   ❌ Python version: {sys.version}")
else:
    print(f"   ✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")

# 2. Check dependencies
print("\n2. Checking dependencies...")
required_modules = [
    "fastapi",
    "uvicorn",
    "motor",
    "beanie",
    "pymongo",
    "pydantic",
    "pandas",
    "numpy",
    "sklearn",
    "xgboost",
    "shap",
    "jose",
    "passlib",
    "reportlab"
]

for module in required_modules:
    try:
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError:
        errors.append(f"Missing module: {module}")
        print(f"   ❌ {module} - NOT INSTALLED")

# 3. Check .env file
print("\n3. Checking environment configuration...")
env_file = Path(".env")
if env_file.exists():
    print("   ✅ .env file exists")
    with open(env_file) as f:
        content = f.read()
        if "MONGODB_URL" in content:
            print("   ✅ MONGODB_URL configured")
        else:
            warnings.append("MONGODB_URL not found in .env")
            print("   ⚠️  MONGODB_URL not found")
else:
    warnings.append(".env file not found")
    print("   ⚠️  .env file not found")

# 4. Check MongoDB connection
print("\n4. Testing MongoDB connection...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    if mongodb_url:
        print(f"   ✅ MongoDB URL configured: {mongodb_url[:50]}...")
        # Try to connect
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            import asyncio
            
            async def test_connection():
                try:
                    client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
                    await client.admin.command('ping')
                    return True
                except Exception as e:
                    return str(e)
            
            result = asyncio.run(test_connection())
            if result is True:
                print("   ✅ MongoDB connection successful")
            else:
                errors.append(f"MongoDB connection failed: {result}")
                print(f"   ❌ MongoDB connection failed: {result}")
        except Exception as e:
            warnings.append(f"Could not test MongoDB: {e}")
            print(f"   ⚠️  Could not test connection: {e}")
    else:
        errors.append("MONGODB_URL not set")
        print("   ❌ MONGODB_URL not set in environment")
except Exception as e:
    warnings.append(f"Error checking MongoDB: {e}")
    print(f"   ⚠️  Error: {e}")

# 5. Check file structure
print("\n5. Checking file structure...")
required_files = [
    "main.py",
    "database.py",
    "models.py",
    "auth.py",
    "schemas.py",
    "ml_bias_detection_production.py",
    "blockchain_service.py",
    "report_generator.py"
]

for file in required_files:
    if Path(file).exists():
        print(f"   ✅ {file}")
    else:
        errors.append(f"Missing file: {file}")
        print(f"   ❌ {file} - NOT FOUND")

# 6. Check syntax
print("\n6. Checking Python syntax...")
try:
    import py_compile
    for file in ["main.py", "database.py", "models.py"]:
        try:
            py_compile.compile(file, doraise=True)
            print(f"   ✅ {file} - syntax OK")
        except py_compile.PyCompileError as e:
            errors.append(f"Syntax error in {file}: {e}")
            print(f"   ❌ {file} - syntax error")
except Exception as e:
    warnings.append(f"Could not check syntax: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if errors:
    print(f"\n❌ ERRORS FOUND: {len(errors)}")
    for error in errors:
        print(f"   • {error}")
    print("\n⚠️  Please fix these errors before starting the server")
else:
    print("\n✅ No critical errors found!")

if warnings:
    print(f"\n⚠️  WARNINGS: {len(warnings)}")
    for warning in warnings:
        print(f"   • {warning}")

if not errors:
    print("\n✅ Backend is ready to start!")
    print("\nTo start the server:")
    print("   python -m uvicorn main:app --reload")
    print("   or")
    print("   python start-server.py")
else:
    print("\n❌ Please fix errors before starting")
    sys.exit(1)

print("=" * 60)

