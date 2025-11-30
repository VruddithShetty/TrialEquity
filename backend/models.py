"""
MongoDB document models using Beanie ODM
"""
from beanie import Document
from pydantic import Field, EmailStr, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class User(Document):
    """
    User document model
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: EmailStr
    username: str
    hashed_password: str
    role: str  # SPONSOR, INVESTIGATOR, REGULATOR, AUDITOR
    organization: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            [("email", 1)],  # Index on email (unique)
            [("username", 1)],  # Index on username (unique)
        ]

class Trial(Document):
    """
    Clinical trial document model
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    filename: str
    uploaded_by: ObjectId  # Reference to User
    status: str = "uploaded"  # uploaded, validated, rejected, on_chain
    participant_count: Optional[int] = None
    metadata: Dict[str, Any]  # Full trial data
    
    # Validation results
    validation_status: Optional[str] = None
    validation_details: Optional[Dict[str, Any]] = None
    
    # ML results
    ml_status: Optional[str] = None  # ACCEPT, REVIEW, REJECT
    ml_score: Optional[float] = None
    ml_details: Optional[Dict[str, Any]] = None
    
    # Blockchain info
    blockchain_tx_hash: Optional[str] = None
    blockchain_status: Optional[str] = None
    blockchain_timestamp: Optional[datetime] = None
    blockchain_block_number: Optional[int] = None
    
    # Digital signature
    digital_signature: Optional[str] = None
    signed_by: Optional[ObjectId] = None  # Reference to User
    signature_timestamp: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "trials"
        indexes = [
            [("blockchain_tx_hash", 1)],  # Index on blockchain hash
            [("uploaded_by", 1)],  # Index on uploaded_by
            [("status", 1)],  # Index on status
            [("ml_status", 1)],  # Index on ML status
        ]

class AuditLog(Document):
    """
    Audit log document model
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    trial_id: ObjectId  # Reference to Trial
    user_id: ObjectId  # Reference to User
    action: str  # upload, validate, ml_check, blockchain_write, verify, etc.
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "audit_logs"
        indexes = [
            [("trial_id", 1)],  # Index on trial_id
            [("user_id", 1)],  # Index on user_id
            [("timestamp", -1)],  # Index on timestamp (descending)
            [("action", 1)],  # Index on action
        ]
