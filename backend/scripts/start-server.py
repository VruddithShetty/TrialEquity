#!/usr/bin/env python3
"""
Start script for backend server with error handling
"""
import sys
import asyncio
import uvicorn
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

async def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    
    try:
        import motor
    except ImportError:
        missing.append("motor")
    
    try:
        import beanie
    except ImportError:
        missing.append("beanie")
    
    try:
        import xgboost
    except ImportError:
        missing.append("xgboost")
    
    if missing:
        print("❌ Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\n📦 Install with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("=" * 60)
    print("Clinical Trials Blockchain Platform - Backend Server")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not asyncio.run(check_dependencies()):
        sys.exit(1)
    print("✅ All dependencies installed")
    print()
    
    # Check .env file
    env_file = backend_path / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("   Create backend/.env with MongoDB connection string")
        print()
    
    # Start server
    print("🚀 Starting backend server...")
    print("   API: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Check if port 8000 is available")
        print("2. Verify MongoDB connection in .env")
        print("3. Check all dependencies are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()

