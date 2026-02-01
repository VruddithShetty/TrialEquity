"""
Tokenization Service for Pseudonymous Trial IDs
"""
import hashlib
import hmac
from typing import Dict, Any
import base64
import os

class TokenizationService:
    """Service for tokenizing trial IDs for pseudonymous auditing"""
    
    def __init__(self, secret_key: str = None):
        # Get from environment or raise error
        if not secret_key:
            secret_key = os.getenv("TOKENIZATION_SECRET_KEY")
            if not secret_key:
                raise ValueError(
                    "TOKENIZATION_SECRET_KEY must be set in environment for secure tokenization"
                )
        
        if len(secret_key) < 32:
            raise ValueError(
                f"TOKENIZATION_SECRET_KEY must be at least 32 characters. "
                f"Current length: {len(secret_key)}"
            )
        self.secret_key = secret_key
    
    def generate_token(self, trial_id: str, user_id: str = None) -> str:
        """
        Generate a pseudonymous token for a trial ID
        This allows cross-study auditing without exposing actual trial IDs
        """
        # Create token data
        token_data = f"{trial_id}:{user_id or 'anonymous'}"
        
        # Generate HMAC-based token
        token = hmac.new(
            self.secret_key.encode('utf-8'),
            token_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Add prefix for identification
        return f"CT_{token[:16]}"
    
    def verify_token(self, token: str, trial_id: str, user_id: str = None) -> bool:
        """
        Verify that a token matches a trial ID
        """
        expected_token = self.generate_token(trial_id, user_id)
        return hmac.compare_digest(token, expected_token)
    
    def get_token_metadata(self, token: str) -> Dict[str, Any]:
        """
        Get metadata about a token (without revealing trial ID)
        """
        return {
            "token": token,
            "token_type": "pseudonymous",
            "created": "tokenized",
            "audit_enabled": True
        }

