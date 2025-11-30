"""
Digital Signature Module for Trial Signing
"""
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any
import json

class DigitalSignatureService:
    """Service for creating and verifying digital signatures"""
    
    @staticmethod
    def generate_signature(trial_data: Dict[str, Any], user_id: str, secret_key: str) -> str:
        """
        Generate a digital signature for trial data
        Uses HMAC-SHA256 for signing
        """
        # Create a canonical representation of the data
        signature_data = {
            "trial_id": trial_data.get("trial_id"),
            "participant_count": trial_data.get("participant_count"),
            "ml_status": trial_data.get("ml_status"),
            "blockchain_tx_hash": trial_data.get("blockchain_tx_hash"),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Convert to JSON string and sign
        message = json.dumps(signature_data, sort_keys=True)
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    @staticmethod
    def verify_signature(
        trial_data: Dict[str, Any],
        signature: str,
        user_id: str,
        secret_key: str
    ) -> Dict[str, Any]:
        """
        Verify a digital signature
        """
        # Regenerate signature
        expected_signature = DigitalSignatureService.generate_signature(
            trial_data, user_id, secret_key
        )
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        return {
            "is_valid": is_valid,
            "signature_match": is_valid,
            "signed_by": user_id,
            "verification_timestamp": datetime.utcnow().isoformat()
        }

