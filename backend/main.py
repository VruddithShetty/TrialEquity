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
from contextlib import asynccontextmanager

from database import init_db, close_db
from models import Trial, User, AuditLog
from schemas import (
    TrialUpload, TrialResponse, MLBiasCheckResponse,
    BlockchainWriteResponse, BlockchainVerifyResponse,
    AuditLogResponse, ModelExplainResponse, ReportResponse,
    UserCreate, LoginRequest
)
from ml_bias_detection_production import MLBiasDetector
from blockchain_service import BlockchainService
from auth import (
    get_current_user, verify_token, check_role,
    require_admin_access, require_uploader_access, require_validator_access,
    require_write_access, require_blockchain_push_access, require_verify_fairness_access,
    is_validator, is_uploader, is_admin
)
from report_generator import ReportGenerator
from digital_signature import DigitalSignatureService
from ipfs_service import IPFSService
from tokenization_service import TokenizationService
from zkp_service import ZKPService
import os
import json
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Starting lifespan...")
    await init_db()
    
    # DO NOT create default test users in production
    # Users must be created through proper admin setup process
    # See SECURITY_SETUP.md for initial admin account creation
    user_count = await User.count()
    print(f"ℹ️ Found {user_count} existing users")
    if user_count == 0:
        print("⚠️  WARNING: No users in database!")
        print("📖 Please refer to SECURITY_SETUP.md to create the first admin user.")
        print("   Run: python setup_admin.py")
    
    # Skip ML initialization during startup to avoid blocking
    # ML models will be loaded lazily when first needed
    print("ℹ️ ML models will be loaded on first use")
    
    yield
    
    # Shutdown
    await close_db()

app = FastAPI(
    title="Clinical Trials Blockchain API",
    description="AI-Enhanced Blockchain Platform for Secure Clinical Trial Data Management",
    version="1.0.0",
    lifespan=lifespan
)

# Database initialization is now handled by lifespan function above
# (Removed deprecated @app.on_event handlers - now using lifespan)

# CORS middleware - configure for production security
# Get allowed origins from environment (comma-separated)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

if not allowed_origins or allowed_origins == ["*"]:
    print("⚠️  WARNING: No ALLOWED_ORIGINS configured. Using localhost defaults.")
    allowed_origins = ["http://localhost:3000", "http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Only allow configured origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],  # Only necessary headers
    expose_headers=["Content-Length", "Content-Type"],  # Only necessary headers
    max_age=600,  # Cache CORS preflight for 10 minutes
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Enable XSS protection (legacy browsers)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Strict Transport Security (enable HTTPS only in production)
    if os.getenv("ENVIRONMENT") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    
    # Remove server info (MutableHeaders doesn't support pop)
    if "server" in response.headers:
        del response.headers["server"]
    if "x-powered-by" in response.headers:
        del response.headers["x-powered-by"]
    
    # Reference policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Feature policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

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
# (Now handled by lifespan event above)

# Initialize ML detector after DB is ready (non-blocking)
# This will train models in background
# print("🔄 Initializing ML models (this may take a few minutes on first run)...")

# (Removed deprecated @app.on_event handlers - now using lifespan)

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

@app.post("/api/admin/users", status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    user_data: UserCreate,
    current_user: dict = Depends(require_admin_access())
):
    """Admin-only: Create a new user (uploader or validator)"""
    from auth import get_password_hash
    
    # Only allow creating UPLOADER or VALIDATOR roles
    if user_data.role not in ["UPLOADER", "VALIDATOR"]:
        raise HTTPException(
            status_code=400, 
            detail="Admin can only create UPLOADER or VALIDATOR users"
        )
    
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
    
    return {
        "message": f"{user_data.role} user created successfully", 
        "user_id": str(user.id),
        "username": user_data.username,
        "email": user_data.email,
        "role": user_data.role
    }

@app.post("/api/login")
async def login(login_data: LoginRequest):
    """Login and get access token"""
    from auth import verify_password, create_access_token
    
    # Find user
    user = await User.find_one(User.email == login_data.email)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
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
    current_user: dict = Depends(require_uploader_access())
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
        
        # Save file to disk for later retrieval
        import tempfile
        temp_dir = tempfile.gettempdir()
        trials_dir = os.path.join(temp_dir, "trials")
        os.makedirs(trials_dir, exist_ok=True)
        
        # Generate unique filename to avoid collisions
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_path = os.path.join(trials_dir, unique_filename)
        
        # Write file content to disk
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Store trial metadata in database with file path
        db_trial = Trial(
            filename=file.filename,
            file_path=file_path,
            uploaded_by=ObjectId(user_id),
            status="uploaded",
            participant_count=trial.get("participant_count", 0),
            metadata=trial
        )
        await db_trial.insert()
        
        # Automatically run ML bias check immediately after upload
        try:
            bias_result = await detector.detect_bias(trial)
            db_trial.ml_status = bias_result["decision"]
            db_trial.ml_score = bias_result["fairness_score"]
            db_trial.ml_details = bias_result
            await db_trial.save()
            
            print(f"✅ ML bias check completed for trial {db_trial.id}: {bias_result['decision']}")
        except Exception as ml_error:
            print(f"⚠️ ML bias check failed for trial {db_trial.id}: {ml_error}")
            # Continue even if ML check fails - report will show pending status
        
        # Generate PDF report immediately (regardless of ML status)
        try:
            # Get uploader info for report
            uploaded_by_user = {
                "username": current_user.get("username", "Unknown"),
                "email": current_user.get("email", "N/A"),
                "role": current_user.get("role", "N/A"),
                "organization": current_user.get("organization")
            }
            
            await report_generator.generate_report(
                trial=db_trial,
                uploaded_by_user=uploaded_by_user,
                audit_logs=[]
            )
            
            print(f"✅ Report generated for trial {db_trial.id}")
        except Exception as report_error:
            print(f"⚠️ Report generation failed for trial {db_trial.id}: {report_error}")
            # Continue even if report generation fails
        
        # Return dict instead of Pydantic model to avoid 422 validation errors
        return {
            "trial_id": str(db_trial.id),
            "filename": file.filename,
            "status": "uploaded",
            "participant_count": db_trial.participant_count,
            "ml_status": db_trial.ml_status,
            "ml_score": db_trial.ml_score,
            "message": "Trial uploaded and analyzed successfully"
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
    current_user: dict = Depends(require_uploader_access())
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
    except (Exception, ValueError):
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
    current_user: dict = Depends(require_uploader_access())
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
    current_user: dict = Depends(require_validator_access())
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
    except (Exception, ValueError):
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
    current_user: dict = Depends(require_blockchain_push_access())
):
    """
    Write validated trial to blockchain
    Only trials with ML status ACCEPT or REVIEW can be written
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot write to blockchain (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Check permissions: uploaders can only push their own trials
    if current_user.get("role") == "UPLOADER":
        if str(trial.uploaded_by) != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Uploaders can only push their own verified trials to blockchain"
            )
    
    if trial.ml_status not in ["ACCEPT", "REVIEW"]:
        error_msg = f"Cannot write trial with status {trial.ml_status} to blockchain. Only ACCEPT or REVIEW trials allowed."
        print(f"❌ Blockchain write failed: {error_msg}")
        raise HTTPException(
            status_code=400,
            detail=error_msg
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
    current_user: dict = Depends(require_validator_access())
):
    """
    Verify trial integrity on blockchain
    Requires: All roles (including AUDITOR for read-only verification)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial.blockchain_tx_hash:
        error_msg = f"Trial {trial_id} ({trial.filename}) has not been written to blockchain yet. Write to blockchain first before verifying."
        print(f"❌ Blockchain verify failed: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
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

@app.get("/api/blockchain/summary-report")
async def download_blockchain_summary(
    current_user: dict = Depends(require_validator_access())
):
    """
    Generate and download a summary PDF of trials written to the blockchain.
    Includes counts of ACCEPT/REVIEW/REJECT and recent written trials.
    Accessible to all authenticated roles.
    """
    try:
        # Fetch trials that have been written to blockchain
        written_trials = await Trial.find(Trial.blockchain_status == "written").to_list()

        # Counts by ML status
        accepted = sum(1 for t in written_trials if t.ml_status == "ACCEPT")
        review = sum(1 for t in written_trials if t.ml_status == "REVIEW")
        rejected = sum(1 for t in written_trials if t.ml_status == "REJECT")

        # By uploader aggregation
        uploader_counts = {}
        for t in written_trials:
            uid = str(t.uploaded_by) if t.uploaded_by else "unknown"
            uploader_counts[uid] = uploader_counts.get(uid, 0) + 1

        # Resolve uploader usernames
        uploader_list = []
        if uploader_counts:
            user_ids = [ObjectId(uid) for uid in uploader_counts.keys() if uid != "unknown"]
            users = await User.find({"_id": {"$in": user_ids}}).to_list()
            name_map = {str(u.id): u.username for u in users}
            for uid, count in uploader_counts.items():
                uploader_list.append({
                    "username": name_map.get(uid, "Unknown"),
                    "count": count
                })

        # Recent trials
        recent = sorted(written_trials, key=lambda t: t.blockchain_timestamp or t.created_at, reverse=True)[:10]
        recent_trials = [{
            "trial_id": str(t.id),
            "filename": t.filename,
            "ml_status": t.ml_status,
            "timestamp": (t.blockchain_timestamp or t.created_at).isoformat() if (t.blockchain_timestamp or t.created_at) else None,
        } for t in recent]

        summary = {
            "total_written": len(written_trials),
            "accepted_count": accepted,
            "review_count": review,
            "rejected_count": rejected,
            "by_uploader": uploader_list,
            "recent_trials": recent_trials,
        }

        # Generate PDF
        pdf_path = report_generator.generate_blockchain_summary(summary)

        # Stream file
        from fastapi.responses import FileResponse
        return FileResponse(pdf_path, media_type="application/pdf", filename="blockchain_summary.pdf")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

# ==================== Regulatory Dashboard ====================

@app.get("/api/admin/audit/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    trial_id: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(require_admin_access())
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

@app.get("/api/trials")
async def get_trials_dashboard(
    status_filter: Optional[str] = None,
    current_user: dict = Depends(require_validator_access())
):
    """
    Unified trials dashboard - visible based on role permissions
    Admin: all trials
    Uploader: only their own trials
    Validator: all trials (read-only)
    """
    
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    # Build query based on role
    if user_role == "ADMIN":
        # Admin sees all trials
        if status_filter:
            trials = await Trial.find(Trial.status == status_filter).to_list()
        else:
            trials = await Trial.find_all().to_list()
    elif user_role == "UPLOADER":
        # Uploader sees only their own trials
        if status_filter:
            trials = await Trial.find(
                Trial.uploaded_by == ObjectId(user_id),
                Trial.status == status_filter
            ).to_list()
        else:
            trials = await Trial.find(Trial.uploaded_by == ObjectId(user_id)).to_list()
    else:  # VALIDATOR
        # Validator sees all trials (read-only)
        if status_filter:
            trials = await Trial.find(Trial.status == status_filter).to_list()
        else:
            trials = await Trial.find_all().to_list()
    
    # Bulk load all unique uploaders to avoid N+1 queries
    unique_uploader_ids = list(set([t.uploaded_by for t in trials if t.uploaded_by]))
    uploaders_map = {}
    
    if unique_uploader_ids:
        uploaders = await User.find({"_id": {"$in": unique_uploader_ids}}).to_list()
        uploaders_map = {str(u.id): u.username for u in uploaders}
    
    # Build response with cached uploader names
    trial_responses = []
    for t in trials:
        uploader_name = uploaders_map.get(str(t.uploaded_by), "Unknown") if t.uploaded_by else "Unknown"
        
        # Determine tamper status and verification
        tamper_status = "Verified" if t.blockchain_status == "written" else "Not on Blockchain"
        blockchain_verified = t.blockchain_status == "written"
        
        trial_responses.append({
            "trial_id": str(t.id),
            "filename": t.filename,
            "uploader": uploader_name,
            "uploader_name": uploader_name,
            "uploaded_by": str(t.uploaded_by) if t.uploaded_by else None,
            "timestamp": t.created_at.isoformat() if t.created_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "fairness_score": t.ml_score,
            "signature_status": "Yes" if t.digital_signature else "No",
            "tamper_status": tamper_status,
            "status": t.status,
            "ml_status": t.ml_status,
            "blockchain_status": t.blockchain_status,
            "blockchain_verified": blockchain_verified,
            "participant_count": t.participant_count
        })
    
    return trial_responses

# ==================== Trial File Management ====================

@app.get("/api/trials/{trial_id}/csv")
async def get_trial_csv_data(
    trial_id: str,
    current_user: dict = Depends(require_validator_access())
):
    """
    Get CSV data for a trial to display in the UI
    Returns headers and rows of the CSV file
    """
    try:
        trial = await Trial.find_one(Trial.id == ObjectId(trial_id))
        if not trial:
            raise HTTPException(status_code=404, detail="Trial not found")
        
        # Check file exists
        file_path = trial.file_path
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="CSV file not found on disk")
        
        # Read CSV file
        import pandas as pd
        df = pd.read_csv(file_path)
        
        # Convert to JSON-serializable format
        headers = df.columns.tolist()
        data = df.to_dict('records')
        
        return {
            "headers": headers,
            "data": data,
            "filename": trial.filename,
            "rows": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV: {str(e)}")

@app.get("/api/trials/{trial_id}/download")
async def download_trial_file(
    trial_id: str,
    current_user: dict = Depends(require_validator_access())
):
    """
    Download the original CSV file for a trial as an attachment.
    Roles: ADMIN, UPLOADER (own files), VALIDATOR (read-only)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")

    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")

    # Uploader can only access own files
    role = current_user.get("role")
    user_id = current_user.get("user_id")
    if role == "UPLOADER" and str(trial.uploaded_by) != str(user_id):
        raise HTTPException(status_code=403, detail="Access denied to this trial")

    file_path = trial.file_path
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="CSV file not found on disk")

    from fastapi.responses import FileResponse
    filename = trial.filename if trial.filename.lower().endswith('.csv') else f"{trial.filename}.csv"
    return FileResponse(file_path, media_type="text/csv", filename=filename)

@app.delete("/api/trials/{trial_id}")
async def delete_trial(
    trial_id: str,
    current_user: dict = Depends(require_validator_access())
):
    """
    Delete a trial
    Admin: can delete any trial
    Uploader: can only delete their own trials
    Validator: cannot delete
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    user_role = current_user.get("role")
    user_id = current_user.get("user_id")
    
    # Check permissions
    if user_role == "VALIDATOR":
        raise HTTPException(
            status_code=403,
            detail="Validators cannot delete trials"
        )
    
    if user_role == "UPLOADER":
        if str(trial.uploaded_by) != user_id:
            raise HTTPException(
                status_code=403,
                detail="Uploaders can only delete their own trials"
            )
    
    # Admin can delete any trial (no check needed)
    
    # Log the deletion
    await AuditLog(
        trial_id=trial.id,
        user_id=ObjectId(user_id),
        action="TRIAL_DELETED",
        details={
            "filename": trial.filename,
            "deleted_by": current_user.get('username'),
            "deleted_by_role": user_role
        }
    ).insert()
    
    # Delete the trial
    await trial.delete()
    
    return {"message": "Trial deleted successfully", "trial_id": trial_id}

@app.get("/api/trials/{trial_id}/download")
async def download_trial_file(
    trial_id: str,
    current_user: dict = Depends(require_validator_access())
):
    """
    Download the original CSV file for a trial
    All authenticated users can download files
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Check if file exists
    if not trial.file_path or not os.path.exists(trial.file_path):
        raise HTTPException(status_code=404, detail="Trial file not found on server")
    
    # Log the download
    await AuditLog(
        trial_id=trial.id,
        user_id=ObjectId(current_user.get("user_id")),
        action="TRIAL_FILE_DOWNLOADED",
        details={
            "filename": trial.filename,
            "downloaded_by": current_user.get('username'),
            "downloaded_by_role": current_user.get('role')
        }
    ).insert()
    
    return FileResponse(
        trial.file_path,
        media_type="text/csv",
        filename=trial.filename
    )

# ==================== Reports ====================

@app.get("/api/downloadReport", response_model=ReportResponse)
async def download_report(
    trial_id: str,
    current_user: dict = Depends(require_validator_access())
):
    """
    Download PDF report for a trial
    Requires: All roles (including AUDITOR for read-only access)
    Generate and download comprehensive trial report (PDF) with all details
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Check permissions: uploaders can only view reports for their own trials
    if current_user.get("role") == "UPLOADER":
        if str(trial.uploaded_by) != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Uploaders can only view reports for their own trials"
            )
    
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
        except (Exception, ValueError):
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
    except (Exception, ValueError):
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
    current_user: dict = Depends(require_validator_access())
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
    current_user: dict = Depends(require_uploader_access())
):
    """
    Digitally sign a trial
    Requires: INVESTIGATOR, REGULATOR, or SPONSOR role
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Check permissions: uploaders can only sign their own trials
    if current_user.get("role") == "UPLOADER":
        if str(trial.uploaded_by) != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Uploaders can only sign their own trials"
            )
    
    # Generate signature
    secret_key = os.getenv("SIGNATURE_SECRET_KEY")
    if not secret_key:
        raise HTTPException(
            status_code=500,
            detail="SIGNATURE_SECRET_KEY not configured in environment"
        )
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
    current_user: dict = Depends(require_validator_access())
):
    """
    Verify a trial's digital signature
    Requires: All roles (including AUDITOR for read-only verification)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial or not trial.digital_signature:
        raise HTTPException(status_code=400, detail="Trial not signed")
    
    # Verify signature
    secret_key = os.getenv("SIGNATURE_SECRET_KEY")
    if not secret_key:
        raise HTTPException(
            status_code=500,
            detail="SIGNATURE_SECRET_KEY not configured in environment"
        )
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
    current_user: dict = Depends(require_uploader_access())
):
    """
    Upload trial data to IPFS for decentralized storage
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot upload to IPFS (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Check permissions: uploaders can only upload their own trials to IPFS
    if current_user.get("role") == "UPLOADER":
        if str(trial.uploaded_by) != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Uploaders can only upload their own trials to IPFS"
            )
    
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
    current_user: dict = Depends(require_validator_access())
):
    """
    Generate a pseudonymous token for a trial ID
    Requires: All roles (including AUDITOR for read-only tokenization)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
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
    current_user: dict = Depends(require_uploader_access())
):
    """
    Generate a Zero-Knowledge Proof for trial data authenticity
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot generate ZKP (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
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
    current_user: dict = Depends(require_validator_access())
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
    except (Exception, ValueError):
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if not trial or "zkp" not in trial.metadata:
        raise HTTPException(status_code=400, detail="No ZKP found for this trial")
    
    # Verify proof
    secret = os.getenv("ZKP_SECRET")
    if not secret:
        raise HTTPException(
            status_code=500, 
            detail="ZKP_SECRET not configured in environment"
        )
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
    current_user: dict = Depends(require_uploader_access())
):
    """
    Trigger a tamper detection alert and notify regulators
    Requires: SPONSOR, INVESTIGATOR, REGULATOR, or ADMIN role
    AUDITOR role cannot trigger alerts (read-only access)
    """
    try:
        trial = await Trial.get(ObjectId(trial_id))
    except (Exception, ValueError):
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

