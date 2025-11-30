"""
Blockchain Service for Hyperledger Fabric, MultiChain, and Quorum
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

class BlockchainService:
    """
    Service for interacting with blockchain networks
    Supports Hyperledger Fabric (primary), MultiChain, and Quorum
    """
    
    def __init__(self):
        self.network_type = "fabric"  # fabric, multichain, quorum
        self.fabric_config = {
            "channel": "clinicaltrials",
            "chaincode": "trialchain",
            "peers": ["peer0.org1.example.com", "peer0.org2.example.com"]
        }
        self.tx_history = {}  # In-memory storage for demo
    
    async def write_trial(
        self, trial_id: str, trial_metadata: Dict[str, Any], hash_data: Any
    ) -> Dict[str, Any]:
        """
        Write trial to blockchain
        In production, this would use actual Fabric SDK
        """
        # Generate hash
        if isinstance(hash_data, dict):
            hash_string = json.dumps(hash_data, sort_keys=True)
        else:
            hash_string = str(hash_data)
        
        data_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        
        # Create transaction
        tx_data = {
            "trial_id": trial_id,
            "hash": data_hash,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "participant_count": trial_metadata.get("participant_count"),
                "ml_status": trial_metadata.get("ml_status", "ACCEPT"),
                "fairness_score": trial_metadata.get("fairness_score", 0.0)
            }
        }
        
        # Simulate blockchain write
        # In production: await self._fabric_invoke("createTrial", tx_data)
        tx_hash = hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()
        
        # Store in history
        self.tx_history[trial_id] = {
            "tx_hash": tx_hash,
            "data_hash": data_hash,
            "timestamp": datetime.utcnow(),
            "block_number": len(self.tx_history) + 1
        }
        
        return {
            "tx_hash": tx_hash,
            "timestamp": datetime.utcnow(),
            "block_number": len(self.tx_history),
            "status": "success"
        }
    
    async def verify_trial(self, trial_id: str, tx_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify trial integrity on blockchain
        """
        if trial_id not in self.tx_history:
            return {
                "is_valid": False,
                "hash_match": False,
                "tamper_detected": True,
                "timestamp": datetime.utcnow(),
                "error": "Trial not found on blockchain"
            }
        
        stored_tx = self.tx_history[trial_id]
        
        # Verify transaction hash
        hash_match = stored_tx["tx_hash"] == tx_hash
        
        # In production, also verify against current blockchain state
        # await self._fabric_query("getTrial", trial_id)
        
        is_valid = hash_match
        
        return {
            "is_valid": is_valid,
            "hash_match": hash_match,
            "tamper_detected": not hash_match,
            "timestamp": datetime.utcnow(),
            "stored_hash": stored_tx["data_hash"]
        }
    
    async def compare_platforms(self) -> Dict[str, Any]:
        """
        Compare Hyperledger Fabric, MultiChain, and Quorum
        """
        comparison = {
            "hyperledger_fabric": {
                "tps": 3500,
                "latency_ms": 2.5,
                "privacy": "High (channels, private data collections)",
                "channels": "Yes (multiple channels supported)",
                "chaincode_expressiveness": "High (Go, Java, Node.js)",
                "regulatory_suitability": "Excellent (permissioned, audit trails)",
                "ease_of_deployment": "Medium (requires setup)",
                "tamper_detection": "Excellent (immutable ledger)",
                "consensus": "Raft, Kafka, Solo",
                "use_case": "Enterprise clinical trials, regulatory compliance"
            },
            "multichain": {
                "tps": 1000,
                "latency_ms": 5.0,
                "privacy": "Medium (streams, permissions)",
                "channels": "No (uses streams instead)",
                "chaincode_expressiveness": "Medium (JSON-based)",
                "regulatory_suitability": "Good (permissioned)",
                "ease_of_deployment": "High (simpler setup)",
                "tamper_detection": "Good (immutable ledger)",
                "consensus": "Round-robin mining",
                "use_case": "Simpler deployments, asset tracking"
            },
            "quorum": {
                "tps": 100,
                "latency_ms": 15.0,
                "privacy": "High (private transactions, Tessera)",
                "channels": "No (uses private transactions)",
                "chaincode_expressiveness": "High (Solidity, EVM)",
                "regulatory_suitability": "Good (permissioned Ethereum)",
                "ease_of_deployment": "Medium (Ethereum-based)",
                "tamper_detection": "Good (immutable ledger)",
                "consensus": "Istanbul BFT, Raft",
                "use_case": "Ethereum-compatible, financial services"
            },
            "summary": {
                "best_tps": "Hyperledger Fabric",
                "best_latency": "Hyperledger Fabric",
                "best_privacy": "Hyperledger Fabric / Quorum",
                "best_regulatory": "Hyperledger Fabric",
                "easiest_deployment": "MultiChain",
                "recommendation": "Hyperledger Fabric for clinical trials due to high TPS, low latency, excellent privacy features, and regulatory suitability"
            }
        }
        
        return comparison
    
    async def _fabric_invoke(self, function_name: str, args: Dict[str, Any]) -> str:
        """
        Invoke Hyperledger Fabric chaincode
        In production, use Fabric SDK
        """
        # Placeholder for actual Fabric SDK call
        # from hfc.fabric import Client
        # client = Client(net_profile="network.json")
        # response = await client.chaincode_invoke(
        #     requestor=requestor,
        #     channel_name=self.fabric_config["channel"],
        #     peers=self.fabric_config["peers"],
        #     fcn=function_name,
        #     args=[json.dumps(args)]
        # )
        return "simulated_tx_hash"
    
    async def _fabric_query(self, function_name: str, args: str) -> Dict[str, Any]:
        """
        Query Hyperledger Fabric chaincode
        """
        # Placeholder for actual Fabric SDK call
        return {}

