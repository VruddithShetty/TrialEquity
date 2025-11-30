# Blockchain Flow Diagram

## Clinical Trial Lifecycle on Blockchain

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIAL UPLOAD                               │
│  Sponsor/Investigator uploads trial dataset                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              PREPROCESSING & VALIDATION                       │
│  - Data cleaning                                             │
│  - Pseudonymization                                          │
│  - Rule engine validation                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ML BIAS DETECTION                               │
│  - Isolation Forest (outlier detection)                      │
│  - XGBoost (bias classification)                           │
│  - Fairness metrics calculation                             │
│  - Statistical tests                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────┴──────────┐
            │                     │
       [ACCEPT]              [REJECT]
            │                     │
            ▼                     ▼
┌──────────────────┐    ┌──────────────────┐
│  BLOCKCHAIN      │    │  BLOCKED          │
│  WRITE           │    │  - Alert sent     │
│                  │    │  - Manual review  │
│  - Generate hash │    └──────────────────┘
│  - Create TX     │
│  - Submit to     │
│    Fabric        │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              CONSENSUS PROCESS                              │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Sponsor  │  │Investigator│ │Regulator │  │ Auditor  │   │
│  │  Node    │  │   Node     │ │  Node    │  │  Node    │   │
│  └────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘   │
│       │              │              │              │         │
│       └──────────────┴──────────────┴──────────────┘         │
│                        │                                      │
│                        ▼                                      │
│              [RAFT CONSENSUS]                                │
│                        │                                      │
│                        ▼                                      │
│              [BLOCK CREATED]                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ON-CHAIN STORAGE                                │
│                                                              │
│  Stored in Blockchain:                                       │
│  - Trial ID                                                  │
│  - SHA256 Hash                                               │
│  - ML Fairness Score                                         │
│  - Timestamp                                                 │
│  - Digital Signature                                          │
│                                                              │
│  Stored Off-Chain (Encrypted):                               │
│  - Full trial dataset                                        │
│  - Participant details (pseudonymized)                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              VERIFICATION & AUDIT                           │
│                                                              │
│  - Hash verification                                         │
│  - Tamper detection                                          │
│  - Regulatory audit logs                                     │
│  - Report generation                                         │
└─────────────────────────────────────────────────────────────┘
```

## Blockchain Network Architecture

```
                    ┌─────────────────┐
                    │   Orderer Node   │
                    │   (Consensus)    │
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
        ┌───────▼────┐  ┌────▼────┐  ┌───▼────┐
        │  Peer 0    │  │ Peer 1  │  │ Peer 2 │
        │  Org 1     │  │ Org 2   │  │ Org 3  │
        │(Sponsor)   │  │(Reg)    │  │(Audit) │
        └────────────┘  └─────────┘  └────────┘
                │            │            │
                └────────────┼────────────┘
                             │
                    ┌────────▼────────┐
                    │  Chaincode      │
                    │  (TrialChain)   │
                    └─────────────────┘
```

## Transaction Flow

1. **Client** submits transaction to peer
2. **Peer** endorses transaction (simulates chaincode)
3. **Client** collects endorsements
4. **Client** submits to orderer
5. **Orderer** creates block
6. **Orderer** distributes to all peers
7. **Peers** validate and commit to ledger

## Data Integrity Verification

```
Current Hash (from DB)
        │
        ▼
    [Compare]
        │
        ├─── Match ───► [Valid] ───► Continue
        │
        └─── Mismatch ───► [Tamper Detected] ───► Alert Regulator
```

## Smart Contract Functions

### TrialChain Chaincode

- `CreateTrial`: Create new trial record
- `GetTrial`: Retrieve trial by ID
- `VerifyTrial`: Verify hash integrity
- `GetAllTrials`: List all trials
- `UpdateTrialStatus`: Update ML status

## Privacy & Channels

Hyperledger Fabric supports:
- **Channels**: Separate ledgers for different organizations
- **Private Data Collections**: Encrypted data visible only to authorized peers
- **Zero-Knowledge Proofs**: Verify data without revealing it

## Consensus Mechanisms

### Raft (Recommended for Clinical Trials)
- Fast finality (~1 second)
- Crash fault tolerant
- Suitable for permissioned networks

### Kafka (Alternative)
- High throughput
- More complex setup
- Better for very large networks

