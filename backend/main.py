"""
FastAPI Backend for Clinical Trials Blockchain System
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
import uvicorn
from bson import ObjectId

from database import init_db, close_db
from models import Trial, User, AuditLog
from schemas import (
    TrialUpload, TrialResponse, MLBiasCheckResponse,
    BlockchainWriteResponse, BlockchainVerifyResponse,
    AuditLogResponse, ModelExplainResponse, ReportResponse,
    UserCreate
)
from ml_bias_detection_production import MLBiasDetector
from blockchain_service import BlockchainService
from auth import (
    get_current_user, verify_token, check_role,
    require_standard_access, require_read_access, require_regulatory_access,
    require_admin_access, require_signing_access, require_write_access,
    is_auditor
)
from report_generator import ReportGenerator
from digital_signature import DigitalSignatureService
from ipfs_service import IPFSService
from tokenization_service import TokenizationService
from zkp_service import ZKPService
import os
import json
from datetime import datetime

app = FastAPI(
    title="Clinical Trials Blockchain API",
    description="AI-Enhanced Blockchain Platform for Secure Clinical Trial Data Management",
    version="1.0.0"
)

# CORS middleware - allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services (lazy initialization)
ml_detector = None
blockchain_service = BlockchainService()
report_generator = ReportGenerator()
ipfs_service = IPFSService()
tokenization_service = TokenizationService()
zkp_service = ZKPService()
digital_signature_service = DigitalSignatureService()

def get_ml_detector():
    """Lazy initialization of ML detector"""
    global ml_detector
    if ml_detector is None:
        ml_detector = MLBiasDetector()
    return ml_detector

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()
    
    # Create default test users if no users exist
    user_count = await User.count()
    if user_count == 0:
        from auth import get_password_hash
        # Create SPONSOR user
        sponsor_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("test123"),
            role="SPONSOR",
            organization="Test Organization"
        )
        await sponsor_user.insert()
        print("✅ Created default SPONSOR user: test@example.com / test123")
        
        # Create REGULATOR user for regulatory features
        regulator_user = User(
            email="regulator@example.com",
            username="regulator",
            hashed_password=get_password_hash("test123"),
            role="REGULATOR",
            organization="FDA Regulatory"
        )
        await regulator_user.insert()
        print("✅ Created default REGULATOR user: regulator@example.com / test123")
    
    # Initialize ML detector after DB is ready (non-blocking)
    # This will train models in background
    print("🔄 Initializing ML models (this may take a few minutes on first run)...")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Clinical Trials Blockchain API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/ml/status")
async def ml_status():
    """Check if ML model is ready"""
    try:
        detector = get_ml_detector()
        return {
            "is_trained": detector.is_trained,
            "model_accuracy": detector.model_accuracy,
            "ensemble_ready": detector.ensemble_model is not None,
            "scaler_ready": detector.scaler is not None,
            "status": "ready" if detector.is_trained else "training"
        }
    except Exception as e:
        return {
            "is_trained": False,
            "error": str(e),
            "status": "error"
        }

# ==================== Authentication ====================

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    from auth import get_password_hash
    
    # Check if user already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = await User.find_one(User.username == user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role,
        organization=user_data.organization
    )
    await user.insert()
    
    return {"message": "User created successfully", "user_id": str(user.id)}

@app.post("/api/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    """Login and get access token"""
    from auth import verify_password, create_access_token
    
    # Find user
    user = await User.find_one(User.email == email)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }

# ==================== Trial Upload & Validation ====================

@app.post("/api/uploadTrial", status_code=status.HTTP_201_CREATED)
async def upload_trial(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_write_access())
):
    """
    Upload a clinical trial dataset and perform initial validation
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot upload trials (read-only access)
    """
    # Explicit check for AUDITOR role with clear error message
    if current_user.get("role") == "AUDITOR":
        raise HTTPException(
            status_code=403,
            detail="AUDITOR role has read-only access. Cannot upload trials."
        )
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file content
        content = await file.read()
        if not content or len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Parse and validate trial data
        # In production, this would parse CSV/JSON/XML from clinicaltrials.gov format
        detector = get_ml_detector()
        trial = await detector.preprocess_trial_data(content, file.filename)
        
        # Validate user_id
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        # Store trial metadata in database
        db_trial = Trial(
            filename=file.filename,
            uploaded_by=ObjectId(user_id),
            status="uploaded",
            participant_count=trial.get("participant_count", 0),
            metadata=trial
        )
        await db_trial.insert()
        
        # Return dict instead of Pydantic model to avoid 422 validation errors
        return {
            "trial_id": str(db_trial.id),
            "filename": file.filename,
            "status": "uploaded",
            "participant_count": db_trial.participant_count,
            "message": "Trial uploaded successfully"
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        import traceback
        error_detail = f"Upload failed: {str(e)}"
        print(f"Upload error: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=error_detail)

@app.post("/api/validateRules")
async def validate_rules(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_standard_access())
):
    """
    Validate trial eligibility rules
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    """
    """
    Validate mandatory eligibility criteria using rule engine
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    detector = get_ml_detector()
    validation_result = await detector.validate_eligibility_rules(trial.metadata)
    
    trial.validation_status = validation_result["status"]
    trial.validation_details = validation_result
    await trial.save()
    
    return validation_result

# ==================== ML Bias Detection ====================

@app.post("/api/runMLBiasCheck", response_model=MLBiasCheckResponse)
async def run_ml_bias_check(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_standard_access())
):
    """
    Run ML bias detection on trial data
    Returns: ACCEPT, REVIEW, or REJECT
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except Exception as e:
        print(f"Error fetching trial: {e}")
        raise HTTPException(status_code=404, detail=f"Trial not found: {str(e)}")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial.metadata:
        raise HTTPException(status_code=400, detail="Trial metadata is missing")
    
    try:
        # Run ML bias detection
        detector = get_ml_detector()
        print(f"Running bias detection on trial {trial_id}...")
        bias_result = await detector.detect_bias(trial.metadata)
        print(f"Bias detection completed: {bias_result.get('decision', 'UNKNOWN')}")
        
        # Update trial status
        trial.ml_status = bias_result["decision"]
        trial.ml_score = bias_result["fairness_score"]
        trial.ml_details = bias_result
        await trial.save()
        
        return MLBiasCheckResponse(
            trial_id=trial_id,
            decision=bias_result["decision"],
            fairness_score=bias_result["fairness_score"],
            metrics=bias_result.get("metrics", {}),
            explanations=bias_result.get("explanations", {}),
            recommendations=bias_result.get("recommendations", []),
            rejection_summary=bias_result.get("rejection_summary")
        )
    except RuntimeError as e:
        # Model not trained yet
        if "not trained" in str(e).lower() or "not initialized" in str(e).lower():
            raise HTTPException(
                status_code=503, 
                detail="ML model is still training. Please wait a moment and try again."
            )
        raise HTTPException(status_code=500, detail=f"ML model error: {str(e)}")
    except ValueError as e:
        # Feature extraction or validation errors
        import traceback
        error_trace = traceback.format_exc()
        print(f"ValueError in bias detection: {error_trace}")
        raise HTTPException(
            status_code=400, 
            detail=f"Bias detection validation error: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR in bias detection: {error_trace}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Bias detection failed: {str(e)}. Check backend logs for details."
        )

@app.post("/api/model/explain", response_model=ModelExplainResponse)
async def explain_model(
    trial_id: str,
    current_user: dict = Depends(require_read_access())
):
    """
    Get SHAP/LIME explanations for ML model decisions
    Requires: All roles (including AUDITOR for read-only access)
    """
    """
    Generate SHAP/LIME explanations for ML model decisions
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    detector = get_ml_detector()
    explanations = await detector.generate_explanations(trial.metadata)
    
    return ModelExplainResponse(
        trial_id=trial_id,
        shap_values=explanations.get("shap", {}),
        lime_explanation=explanations.get("lime", {}),
        feature_importance=explanations.get("feature_importance", {})
    )

# ==================== Blockchain Operations ====================

@app.post("/api/blockchain/write", response_model=BlockchainWriteResponse)
async def write_to_blockchain(
    trial_id: str,
    current_user: dict = Depends(require_write_access())
):
    """
    Write validated trial to blockchain
    Only trials with ML status ACCEPT or REVIEW can be written
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot write to blockchain (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if trial.ml_status not in ["ACCEPT", "REVIEW"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot write trial with status {trial.ml_status} to blockchain"
        )
    
    # Generate hash and write to blockchain
    result = await blockchain_service.write_trial(
        trial_id=trial_id,
        trial_metadata=trial.metadata,
        hash_data=trial.metadata
    )
    
    # Update trial with blockchain info
    trial.blockchain_tx_hash = result["tx_hash"]
    trial.blockchain_status = "written"
    trial.blockchain_timestamp = result["timestamp"]
    await trial.save()
    
    # Log audit event
    audit_log = AuditLog(
        trial_id=ObjectId(trial_id),
        user_id=ObjectId(current_user["user_id"]),
        action="blockchain_write",
        details=result
    )
    await audit_log.insert()
    
    return BlockchainWriteResponse(
        trial_id=trial_id,
        tx_hash=result["tx_hash"],
        block_number=result.get("block_number"),
        timestamp=result["timestamp"],
        status="success"
    )

@app.post("/api/blockchain/verify", response_model=BlockchainVerifyResponse)
async def verify_blockchain(
    trial_id: str,
    current_user: dict = Depends(require_read_access())
):
    """
    Verify trial integrity on blockchain
    Requires: All roles (including AUDITOR for read-only verification)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial.blockchain_tx_hash:
        raise HTTPException(status_code=400, detail="Trial not written to blockchain")
    
    verification = await blockchain_service.verify_trial(
        trial_id=trial_id,
        tx_hash=trial.blockchain_tx_hash if trial.blockchain_tx_hash else None
    )
    
    # If tamper detected, trigger alert and notify regulators immediately
    if verification.get("tamper_detected"):
        try:
            regulators = await User.find(User.role == "REGULATOR").to_list()
            # Create critical alert
            alert_log = AuditLog(
                trial_id=ObjectId(trial_id),
                user_id=ObjectId(current_user["user_id"]),
                action="tamper_alert",
                details={
                    "alert_type": "tamper_detected",
                    "severity": "critical",
                    "message": f"Tampering detected in trial {trial_id}",
                    "regulators_notified": len(regulators),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            await alert_log.insert()
            print(f"🚨 TAMPER ALERT: Trial {trial_id} - Notifying {len(regulators)} regulators")
        except Exception as e:
            print(f"Error notifying regulators: {e}")
    
    # Log verification
    audit_log = AuditLog(
        trial_id=ObjectId(trial_id),
        user_id=ObjectId(current_user["user_id"]),
        action="blockchain_verify",
        details=verification
    )
    await audit_log.insert()
    
    return BlockchainVerifyResponse(
        trial_id=trial_id,
        is_valid=verification["is_valid"],
        hash_match=verification["hash_match"],
        tamper_detected=verification.get("tamper_detected", False),
        verification_timestamp=verification["timestamp"]
    )

# ==================== Regulatory Dashboard ====================

@app.get("/api/regulator/audit/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    trial_id: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(require_regulatory_access())
):
    """
    Get audit logs for regulatory review
    Requires: REGULATOR role only
    """
    
    if trial_id:
        logs = await AuditLog.find(AuditLog.trial_id == ObjectId(trial_id)).sort([("timestamp", -1)]).limit(limit).to_list()
    else:
        logs = await AuditLog.find_all().sort([("timestamp", -1)]).limit(limit).to_list()
    
    return [AuditLogResponse(
        log_id=str(log.id),
        trial_id=str(log.trial_id),
        user_id=str(log.user_id),
        action=log.action,
        timestamp=log.timestamp.isoformat(),
        details=log.details
    ) for log in logs]

@app.get("/api/regulator/trials")
async def get_all_trials(
    status_filter: Optional[str] = None,
    current_user: dict = Depends(require_regulatory_access())
):
    """
    Get all trials for regulatory review
    Requires: REGULATOR role only
    """
    
    if status_filter:
        trials = await Trial.find(Trial.status == status_filter).to_list()
    else:
        trials = await Trial.find_all().to_list()
    
    return [TrialResponse(
        trial_id=str(t.id),
        filename=t.filename,
        status=t.status,
        participant_count=t.participant_count,
        ml_status=t.ml_status,
        blockchain_status=t.blockchain_status
    ) for t in trials]

# ==================== Reports ====================

@app.get("/api/downloadReport", response_model=ReportResponse)
async def download_report(
    trial_id: str,
    current_user: dict = Depends(require_read_access())
):
    """
    Download PDF report for a trial
    Requires: All roles (including AUDITOR for read-only access)
    Generate and download comprehensive trial report (PDF) with all details
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Get uploaded by user information
    uploaded_by_user = None
    if trial.uploaded_by:
        try:
            user = await User.get(trial.uploaded_by)
            uploaded_by_user = {
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "organization": user.organization
            }
        except:
            pass  # User not found, continue without user info
    
    # Get audit logs for this trial
    audit_logs = []
    try:
        logs = await AuditLog.find(AuditLog.trial_id == ObjectId(trial_id)).sort([("timestamp", -1)]).limit(50).to_list()
        audit_logs = [{
            "log_id": str(log.id),
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "action": log.action,
            "user_id": str(log.user_id),
            "details": log.details
        } for log in logs]
    except:
        pass  # Continue without audit logs if there's an error
    
    # Generate comprehensive PDF report with all details
    report_path = await report_generator.generate_report(
        trial=trial,
        uploaded_by_user=uploaded_by_user,
        audit_logs=audit_logs
    )
    
    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=f"trial_report_{trial_id}.pdf"
    )

# ==================== Blockchain Comparison ====================

@app.get("/api/blockchain/compare")
async def compare_blockchains(
    current_user: dict = Depends(require_read_access())
):
    """
    Compare different blockchain platforms
    Requires: All roles (including AUDITOR for read-only access)
    """
    """
    Compare Hyperledger Fabric, MultiChain, and Quorum
    """
    comparison = await blockchain_service.compare_platforms()
    return comparison

# ==================== Digital Signatures ====================

@app.post("/api/trial/sign")
async def sign_trial(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_signing_access())
):
    """
    Digitally sign a trial
    Requires: INVESTIGATOR, REGULATOR, or SPONSOR role
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Generate signature
    secret_key = os.getenv("SIGNATURE_SECRET_KEY", "default-signature-key")
    trial_data = {
        "trial_id": str(trial.id),
        "participant_count": trial.participant_count,
        "ml_status": trial.ml_status,
        "blockchain_tx_hash": trial.blockchain_tx_hash
    }
    
    signature = digital_signature_service.generate_signature(
        trial_data,
        current_user["user_id"],
        secret_key
    )
    
    # Update trial
    trial.digital_signature = signature
    trial.signed_by = ObjectId(current_user["user_id"])
    trial.signature_timestamp = datetime.utcnow()
    await trial.save()
    
    # Log audit event
    audit_log = AuditLog(
        trial_id=ObjectId(trial_id),
        user_id=ObjectId(current_user["user_id"]),
        action="trial_signed",
        details={"signature": signature[:20] + "..."}
    )
    await audit_log.insert()
    
    return {
        "trial_id": trial_id,
        "signature": signature,
        "signed_by": current_user["user_id"],
        "signature_timestamp": trial.signature_timestamp.isoformat(),
        "status": "signed"
    }

@app.post("/api/trial/verify-signature")
async def verify_trial_signature(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_read_access())
):
    """
    Verify a trial's digital signature
    Requires: All roles (including AUDITOR for read-only verification)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial or not trial.digital_signature:
        raise HTTPException(status_code=400, detail="Trial not signed")
    
    # Verify signature
    secret_key = os.getenv("SIGNATURE_SECRET_KEY", "default-signature-key")
    trial_data = {
        "trial_id": str(trial.id),
        "participant_count": trial.participant_count,
        "ml_status": trial.ml_status,
        "blockchain_tx_hash": trial.blockchain_tx_hash
    }
    
    verification = digital_signature_service.verify_signature(
        trial_data,
        trial.digital_signature,
        str(trial.signed_by) if trial.signed_by else "",
        secret_key
    )
    
    return {
        "trial_id": trial_id,
        "signature_valid": verification["is_valid"],
        "signed_by": str(trial.signed_by) if trial.signed_by else None,
        "signature_timestamp": trial.signature_timestamp.isoformat() if trial.signature_timestamp else None,
        "verification": verification
    }

# ==================== IPFS Integration ====================

@app.post("/api/ipfs/upload")
async def upload_to_ipfs(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_write_access())
):
    """
    Upload trial data to IPFS for decentralized storage
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot upload to IPFS (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Convert trial metadata to bytes
    trial_json = json.dumps(trial.metadata, sort_keys=True)
    content = trial_json.encode('utf-8')
    
    # Upload to IPFS
    result = await ipfs_service.upload_file(content, f"trial_{trial_id}.json")
    
    # Store IPFS hash in trial (add to metadata)
    if "ipfs" not in trial.metadata:
        trial.metadata["ipfs"] = {}
    trial.metadata["ipfs"]["hash"] = result["ipfs_hash"]
    trial.metadata["ipfs"]["url"] = result["ipfs_url"]
    await trial.save()
    
    return {
        "trial_id": trial_id,
        "ipfs_hash": result["ipfs_hash"],
        "ipfs_url": result["ipfs_url"],
        "status": result["status"]
    }

# ==================== Tokenization ====================

@app.post("/api/trial/tokenize")
async def tokenize_trial(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_read_access())
):
    """
    Generate a pseudonymous token for a trial ID
    Requires: All roles (including AUDITOR for read-only tokenization)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Generate token
    token = tokenization_service.generate_token(
        str(trial.id),
        current_user["user_id"]
    )
    
    return {
        "trial_id": trial_id,
        "token": token,
        "metadata": tokenization_service.get_token_metadata(token)
    }

# ==================== Zero-Knowledge Proofs ====================

@app.post("/api/zkp/generate")
async def generate_zkp(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_write_access())
):
    """
    Generate a Zero-Knowledge Proof for trial data authenticity
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot generate ZKP (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Generate ZKP
    secret = os.getenv("ZKP_SECRET", "default-zkp-secret")
    trial_data = {
        "participant_count": trial.participant_count,
        "ml_status": trial.ml_status,
        "ml_score": trial.ml_score
    }
    
    proof = zkp_service.generate_proof(trial_data, secret)
    
    # Store proof in trial metadata
    if "zkp" not in trial.metadata:
        trial.metadata["zkp"] = {}
    trial.metadata["zkp"]["proof"] = proof
    await trial.save()
    
    return {
        "trial_id": trial_id,
        "proof": proof,
        "status": "generated"
    }

@app.post("/api/zkp/verify")
async def verify_zkp(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_read_access())
):
    """
    Verify a Zero-Knowledge Proof
    Requires: All roles (including AUDITOR for read-only verification)
    """
    """
    Verify a Zero-Knowledge Proof without exposing PHI
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial or "zkp" not in trial.metadata:
        raise HTTPException(status_code=400, detail="No ZKP found for this trial")
    
    # Verify proof
    secret = os.getenv("ZKP_SECRET", "default-zkp-secret")
    trial_data = {
        "participant_count": trial.participant_count,
        "ml_status": trial.ml_status,
        "ml_score": trial.ml_score
    }
    
    proof = trial.metadata["zkp"]["proof"]
    verification = zkp_service.verify_proof(proof, trial_data, secret)
    
    return {
        "trial_id": trial_id,
        "verification": verification
    }

# ==================== Admin Panel ====================

@app.get("/api/admin/nodes")
async def get_nodes(
    current_user: dict = Depends(require_admin_access())
):
    """
    Get blockchain node status
    Requires: REGULATOR or ADMIN role
    """
    nodes = [
        {
            "name": "Sponsor Node",
            "address": "peer0.org1.example.com",
            "status": "online",
            "role": "SPONSOR"
        },
        {
            "name": "Regulator Node",
            "address": "peer0.org2.example.com",
            "status": "online",
            "role": "REGULATOR"
        },
        {
            "name": "Investigator Node",
            "address": "peer0.org3.example.com",
            "status": "online",
            "role": "INVESTIGATOR"
        },
        {
            "name": "Auditor Node",
            "address": "peer0.org4.example.com",
            "status": "online",
            "role": "AUDITOR"
        }
    ]
    return {"nodes": nodes}

@app.get("/api/admin/users")
async def get_users(
    current_user: dict = Depends(require_admin_access())
):
    """
    Get all users in the system
    Requires: REGULATOR or ADMIN role
    """
    users = await User.find_all().to_list()
    return {
        "users": [
            {
                "user_id": str(u.id),
                "email": u.email,
                "username": u.username,
                "role": u.role,
                "organization": u.organization
            }
            for u in users
        ]
    }

@app.post("/api/admin/retrain-model")
async def retrain_model(
    current_user: dict = Depends(require_admin_access())
):
    """
    Trigger ML model retraining
    Requires: REGULATOR or ADMIN role
    """
    # In production, this would trigger async model retraining
    global ml_detector
    ml_detector = None  # Reset to trigger retraining on next use
    
    return {
        "status": "retraining_triggered",
        "message": "Model retraining has been triggered. This may take several minutes."
    }

# ==================== Real-Time Alerts ====================

@app.post("/api/alerts/tamper")
async def trigger_tamper_alert(
    trial_id: str = Query(...),
    current_user: dict = Depends(require_standard_access())
):
    """
    Trigger a tamper detection alert and notify regulators
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot trigger alerts (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Create alert
    alert = AuditLog(
        trial_id=ObjectId(trial_id),
        user_id=ObjectId(current_user["user_id"]),
        action="tamper_alert",
        details={
            "alert_type": "tamper_detected",
            "severity": "critical",
            "message": f"Tampering detected in trial {trial_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    await alert.insert()
    
    # Notify regulators (in production, this would send emails/notifications)
    regulators = await User.find(User.role == "REGULATOR").to_list()
    
    return {
        "trial_id": trial_id,
        "alert_created": True,
        "regulators_notified": len(regulators),
        "alert_id": str(alert.id)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

