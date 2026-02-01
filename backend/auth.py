"""
Authentication and authorization module
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# SECURITY: SECRET_KEY must be set in environment - no default fallback
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "CRITICAL SECURITY ERROR: SECRET_KEY not set in environment!\n"
        "Set a strong SECRET_KEY (min 32 characters) in your .env file:\n"
        "  SECRET_KEY=<your-strong-random-key-here>\n"
        "  Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

if len(SECRET_KEY) < 32:
    raise ValueError(
        f"SECURITY ERROR: SECRET_KEY must be at least 32 characters. "
        f"Current length: {len(SECRET_KEY)}"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Validate token expiration
if ACCESS_TOKEN_EXPIRE_MINUTES > 1440:  # Max 24 hours
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed 1440 (24 hours)")

# Use bcrypt directly to avoid passlib compatibility issues
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Try using bcrypt directly first
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        # Fallback to passlib if needed
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return pwd_context.verify(plain_password, hashed_password)
        except:
            return False

def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        # Use bcrypt directly
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        # Fallback to passlib if needed
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, str]:
    """Verify JWT token and return user info"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None:
            raise credentials_exception
        
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise credentials_exception

async def get_current_user(user_info: Dict = Depends(verify_token)) -> Dict[str, str]:
    """Dependency for getting current authenticated user"""
    return user_info

def check_role(allowed_roles: list):
    """Decorator factory for role-based access control"""
    def role_checker(current_user: Dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

# Role definitions for RBAC
ROLES = {
    "ADMIN": "System administrators with complete access to all trials, reports, and blockchain data. Can verify fairness and push approved trials to blockchain.",
    "UPLOADER": "Users who can upload trials, run fairness tests, push only their own verified trials to blockchain, and view only the data they personally uploaded.",
    "VALIDATOR": "Users with read-only access to view all trials and reports to verify integrity and detect tampering."
}

# Role-based permissions
# Admin operations: complete access
ADMIN_OPERATIONS = ["ADMIN"]
# Uploader operations: upload, run ML tests, push own trials, view own data
UPLOADER_OPERATIONS = ["ADMIN", "UPLOADER"]
# Validator operations: read-only access to all trials and reports
VALIDATOR_OPERATIONS = ["ADMIN", "UPLOADER", "VALIDATOR"]
# Write operations: cannot be done by validators
WRITE_OPERATIONS = ["ADMIN", "UPLOADER"]
# Blockchain push operations: admin can push any, uploader only own
BLOCKCHAIN_PUSH_OPERATIONS = ["ADMIN", "UPLOADER"]
# Verify fairness operations: admin only
VERIFY_FAIRNESS_OPERATIONS = ["ADMIN"]

def require_admin_access():
    """Require admin access (ADMIN only)"""
    return check_role(ADMIN_OPERATIONS)

def require_uploader_access():
    """Require uploader access (ADMIN, UPLOADER)"""
    return check_role(UPLOADER_OPERATIONS)

def require_validator_access():
    """Require validator access (ADMIN, UPLOADER, VALIDATOR)"""
    return check_role(VALIDATOR_OPERATIONS)

def require_write_access():
    """Require write access (ADMIN, UPLOADER)"""
    return check_role(WRITE_OPERATIONS)

def require_blockchain_push_access():
    """Require blockchain push access (ADMIN, UPLOADER)"""
    return check_role(BLOCKCHAIN_PUSH_OPERATIONS)

def require_verify_fairness_access():
    """Require verify fairness access (ADMIN only)"""
    return check_role(VERIFY_FAIRNESS_OPERATIONS)

def is_validator(current_user: Dict = Depends(get_current_user)) -> bool:
    """Check if current user is a validator (read-only)"""
    return current_user.get("role") == "VALIDATOR"

def is_uploader(current_user: Dict = Depends(get_current_user)) -> bool:
    """Check if current user is an uploader"""
    return current_user.get("role") == "UPLOADER"

def is_admin(current_user: Dict = Depends(get_current_user)) -> bool:
    """Check if current user is an admin"""
    return current_user.get("role") == "ADMIN"

