"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List, Any
from datetime import datetime

class TrialUpload(BaseModel):
    filename: str
    participant_count: Optional[int] = None

class TrialResponse(BaseModel):
    trial_id: str
    filename: str
    status: str
    participant_count: Optional[int] = None
    ml_status: Optional[str] = None
    blockchain_status: Optional[str] = None
    message: Optional[str] = None

class MLBiasCheckResponse(BaseModel):
    trial_id: str
    decision: str  # ACCEPT, REVIEW, REJECT
    fairness_score: float
    metrics: Dict[str, Any]
    explanations: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    rejection_summary: Optional[str] = None  # Clear explanation if rejected

class BlockchainWriteResponse(BaseModel):
    trial_id: str
    tx_hash: str
    block_number: Optional[int] = None
    timestamp: datetime
    status: str

class BlockchainVerifyResponse(BaseModel):
    trial_id: str
    is_valid: bool
    hash_match: bool
    tamper_detected: bool
    verification_timestamp: datetime

class AuditLogResponse(BaseModel):
    log_id: str
    trial_id: str
    user_id: str
    action: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class ModelExplainResponse(BaseModel):
    trial_id: str
    shap_values: Dict[str, Any]
    lime_explanation: Dict[str, Any]
    feature_importance: Dict[str, Any]

class ReportResponse(BaseModel):
    trial_id: str
    report_url: str
    generated_at: datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str
    organization: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    role: str
    organization: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
