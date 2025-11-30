# System Architecture

## Overview

The Clinical Trials Blockchain Platform is a comprehensive system that combines machine learning, blockchain technology, and modern web interfaces to ensure secure, fair, and regulatory-compliant clinical trial data management.

## System Components

### 1. Frontend (Next.js)
- **Technology**: Next.js 14, TypeScript, Tailwind CSS, ShadCN UI
- **Pages**:
  - Landing Page
  - Upload Page
  - ML Analysis Page
  - Blockchain Operations Page
  - Regulator Dashboard
  - Blockchain Comparison Page

### 2. Backend (FastAPI)
- **Technology**: Python FastAPI, SQLAlchemy, PostgreSQL
- **Key Modules**:
  - ML Bias Detection
  - Blockchain Service
  - Authentication & Authorization
  - Report Generation
  - API Endpoints

### 3. ML Models
- **Algorithms**:
  - Isolation Forest (outlier detection)
  - XGBoost (classification)
  - Statistical tests (Chi-square, KS test)
  - SHAP/LIME (explainability)

### 4. Blockchain Layer
- **Primary**: Hyperledger Fabric
- **Comparisons**: MultiChain, Quorum
- **Chaincode**: Go-based smart contracts

## Data Flow

```
1. Trial Upload
   ↓
2. Preprocessing & Validation
   ↓
3. ML Bias Detection
   ↓
4. Decision (ACCEPT/REVIEW/REJECT)
   ↓
5. Blockchain Write (if accepted)
   ↓
6. Hash Verification
   ↓
7. Regulatory Audit
```

## Security Features

- **Zero-Knowledge Proofs**: For data authenticity without exposing PHI
- **Digital Signatures**: Cryptographic signing of trial submissions
- **Role-Based Access Control**: Regulator, Sponsor, Investigator, Auditor roles
- **Encrypted Storage**: Off-chain encrypted file storage
- **Tamper Detection**: Real-time hash verification

## Deployment Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  PostgreSQL │
│  (Next.js)  │     │  (FastAPI)  │     │  (Database) │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  Blockchain  │
                    │  (Fabric)   │
                    └─────────────┘
```

## ML Model Architecture

### Bias Detection Pipeline

1. **Feature Extraction**: Age, gender, ethnicity, sample size, eligibility scores
2. **Outlier Detection**: Isolation Forest identifies unusual patterns
3. **Classification**: XGBoost predicts bias probability
4. **Fairness Metrics**: Demographic parity, disparate impact, equality of opportunity
5. **Statistical Tests**: Chi-square for distribution validation
6. **Explainability**: SHAP/LIME for interpretable results

### Decision Logic

- **ACCEPT**: Fairness score ≥ 0.8, not outlier, bias probability < 0.3
- **REVIEW**: Fairness score ≥ 0.6, bias probability < 0.5
- **REJECT**: Otherwise

## Blockchain Architecture

### Hyperledger Fabric Network

- **Organizations**: Sponsor, Investigator, Regulator, Auditor
- **Channels**: Clinical trials channel
- **Chaincode**: TrialChain (Go)
- **Consensus**: Raft

### On-Chain Storage

- Trial metadata
- SHA256 hash of trial data
- ML fairness scores
- Timestamps
- Digital signatures

### Off-Chain Storage

- Encrypted trial datasets
- Large files (IPFS optional)

## API Endpoints

### Trial Management
- `POST /api/uploadTrial` - Upload trial dataset
- `POST /api/validateRules` - Validate eligibility rules
- `POST /api/runMLBiasCheck` - Run ML bias detection

### Blockchain
- `POST /api/blockchain/write` - Write to blockchain
- `POST /api/blockchain/verify` - Verify integrity
- `GET /api/blockchain/compare` - Compare platforms

### Regulatory
- `GET /api/regulator/audit/logs` - Get audit logs
- `GET /api/regulator/trials` - Get all trials

### Reports
- `GET /api/downloadReport` - Download PDF report
- `POST /api/model/explain` - Get ML explanations

## Scalability Considerations

- **Horizontal Scaling**: Stateless API design
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session management
- **Blockchain**: Fabric network can scale with additional peers
- **ML Models**: Can be deployed as separate microservices

## Compliance & Regulatory

- **GDPR**: Data pseudonymization
- **HIPAA**: Encrypted storage, access controls
- **FDA**: Audit trails, digital signatures
- **GCP**: Good Clinical Practice compliance

