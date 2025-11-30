"""
IPFS Service for Decentralized Storage
"""
import requests
import json
import hashlib
from typing import Dict, Any, Optional
import os

class IPFSService:
    """Service for interacting with IPFS"""
    
    def __init__(self):
        self.ipfs_url = os.getenv("IPFS_URL", "http://localhost:5001")
        # Use public gateway as fallback
        self.ipfs_gateway = os.getenv("IPFS_GATEWAY", "https://ipfs.io/ipfs")
    
    async def upload_file(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Upload file to IPFS
        Returns IPFS hash (CID)
        """
        try:
            # Prepare multipart form data
            files = {
                'file': (filename, content)
            }
            
            # Upload to IPFS
            response = requests.post(
                f"{self.ipfs_url}/api/v0/add",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result.get("Hash")
                
                return {
                    "ipfs_hash": ipfs_hash,
                    "ipfs_url": f"{self.ipfs_gateway}/{ipfs_hash}",
                    "filename": filename,
                    "size": len(content),
                    "status": "success"
                }
            else:
                raise Exception(f"IPFS upload failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            # IPFS not available, return mock data
            # Generate a hash that looks like an IPFS CID (Qm... format)
            content_hash = hashlib.sha256(content).hexdigest()
            # IPFS CID format starts with Qm (CIDv0) or b (CIDv1)
            # Create a mock hash that looks like a valid CIDv0 (starts with Qm, then base58-like chars)
            # Use first 44 chars of hex as a placeholder (real CIDv0 is 46 chars starting with Qm)
            mock_hash = "Qm" + content_hash[:44]
            # Use public IPFS gateway for mock data (link won't work but shows format)
            public_gateway = "https://ipfs.io/ipfs"
            return {
                "ipfs_hash": mock_hash,
                "ipfs_url": f"{public_gateway}/{mock_hash}",
                "filename": filename,
                "size": len(content),
                "status": "mock",  # Indicates IPFS not available
                "gateway": public_gateway,
                "note": "IPFS not available locally. This is a demonstration hash."
            }
        except Exception as e:
            raise Exception(f"IPFS upload error: {str(e)}")
    
    async def retrieve_file(self, ipfs_hash: str) -> bytes:
        """
        Retrieve file from IPFS by hash
        """
        try:
            response = requests.get(
                f"{self.ipfs_gateway}/{ipfs_hash}",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"IPFS retrieval failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"IPFS retrieval error: {str(e)}")
    
    async def pin_file(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Pin file in IPFS to prevent garbage collection
        """
        try:
            response = requests.post(
                f"{self.ipfs_url}/api/v0/pin/add",
                params={"arg": ipfs_hash},
                timeout=30
            )
            
            if response.status_code == 200:
                return {"status": "pinned", "ipfs_hash": ipfs_hash}
            else:
                raise Exception(f"IPFS pin failed: {response.status_code}")
        except Exception as e:
            return {"status": "error", "error": str(e)}

