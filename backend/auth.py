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

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
    "SPONSOR": "Pharmaceutical companies or organizations funding clinical trials",
    "INVESTIGATOR": "Researchers conducting clinical trials",
    "REGULATOR": "Regulatory authorities overseeing compliance (FDA, EMA, etc.)",
    "ADMIN": "System administrators managing infrastructure",
    "AUDITOR": "External auditors with read-only access"
}

# Role-based permissions
# Standard operations: upload, validate, ML check, blockchain write, sign, download reports
STANDARD_OPERATIONS = ["SPONSOR", "INVESTIGATOR", "REGULATOR", "ADMIN"]
# Read-only operations: verify blockchain, download reports, view data
READ_ONLY_OPERATIONS = ["SPONSOR", "INVESTIGATOR", "REGULATOR", "ADMIN", "AUDITOR"]
# Regulatory oversight: view audit logs, all trials
REGULATORY_OPERATIONS = ["REGULATOR"]
# Admin operations: manage nodes, users, retrain models
ADMIN_OPERATIONS = ["REGULATOR", "ADMIN"]
# Signing operations: investigators, regulators, sponsors can sign
SIGNING_OPERATIONS = ["INVESTIGATOR", "REGULATOR", "SPONSOR"]
# Write operations: cannot be done by auditors
WRITE_OPERATIONS = ["SPONSOR", "INVESTIGATOR", "REGULATOR", "ADMIN"]

def require_standard_access():
    """Require standard user access (SPONSOR, INVESTIGATOR, REGULATOR, ADMIN)"""
    return check_role(STANDARD_OPERATIONS)

def require_read_access():
    """Require read access (all roles including AUDITOR)"""
    return check_role(READ_ONLY_OPERATIONS)

def require_regulatory_access():
    """Require regulatory access (REGULATOR only)"""
    return check_role(REGULATORY_OPERATIONS)

def require_admin_access():
    """Require admin access (REGULATOR or ADMIN)"""
    return check_role(ADMIN_OPERATIONS)

def require_signing_access():
    """Require signing access (INVESTIGATOR, REGULATOR, SPONSOR)"""
    return check_role(SIGNING_OPERATIONS)

def require_write_access():
    """Require write access (cannot be AUDITOR)"""
    return check_role(WRITE_OPERATIONS)

def is_auditor(current_user: Dict = Depends(get_current_user)) -> bool:
    """Check if current user is an auditor (read-only)"""
    return current_user.get("role") == "AUDITOR"

