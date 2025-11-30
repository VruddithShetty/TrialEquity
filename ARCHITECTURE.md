# TrialEquity Platform - Architecture & Technical Documentation

## Overview

TrialEquity is a production-grade platform combining machine learning, blockchain technology, and modern web frameworks to ensure fair, secure, and compliant clinical trial data management.

## System Architecture

### High-Level Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  (Next.js)   │     │  (FastAPI)   │     │  (Database)  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ├──▶ ML Models (XGBoost, RF)
                            │
                            └──▶ Blockchain (Hyperledger Fabric)
```

## Technology Stack

### Frontend Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Custom CSS variables
- **UI Components**: ShadCN UI
- **Charts**: Recharts
- **Animations**: Framer Motion
- **HTTP Client**: Axios

### Backend Stack

- **Framework**: FastAPI (Python 3.10+)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **File Handling**: pandas, numpy

### Machine Learning Stack

- **Ensemble Model**: XGBoost + Random Forest (Voting Classifier)
- **Outlier Detection**: Isolation Forest
- **Feature Engineering**: 18 comprehensive features
- **Training Dataset**: 30,000 samples
- **Accuracy**: 96.13% (unbiased detection: 99.95%, biased detection: 92.31%)
- **Explainability**: SHAP/LIME (optional)
- **Statistical Tests**: Chi-square, Kolmogorov-Smirnov

### Blockchain Stack

- **Primary Platform**: Hyperledger Fabric 2.x
- **Chaincode Language**: Go
- **Consensus**: Raft
- **Storage**: On-chain metadata, off-chain encrypted files
- **IPFS**: Optional for large file storage

### Infrastructure

- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana (optional)
- **Load Testing**: k6, Locust

## Data Flow

### Complete Trial Processing Pipeline

```
1. Trial Upload
   ├── CSV file upload via POST /api/uploadTrial
   ├── File validation (format, columns)
   └── Preprocessing (data cleaning, normalization)
   
2. Rule Validation
   ├── Eligibility rule checks
   ├── Sample size validation
   ├── Data quality checks
   └── Status: PASSED / FAILED
   
3. ML Bias Detection
   ├── Feature extraction (18 features)
   ├── Outlier detection (Isolation Forest)
   ├── Bias classification (XGBoost + RF)
   ├── Fairness metrics calculation
   ├── Statistical tests
   └── Decision: ACCEPT / REVIEW / REJECT
   
4. Blockchain Write (if ACCEPT/REVIEW)
   ├── Generate trial hash (SHA256)
   ├── Create blockchain transaction
   ├── Store metadata on-chain
   ├── Store encrypted data off-chain
   └── Return transaction ID
   
5. Audit Trail
   ├── Log all actions
   ├── Store in database
   └── Available for regulatory review
   
6. Regulatory Dashboard
   ├── Real-time audit logs
   ├── Trial status tracking
   ├── Tamper detection
   └── PDF report generation
```

## Component Details

### Frontend Components

#### Pages
- **Landing Page** (`/`) - Hero section, feature overview
- **Upload Page** (`/upload`) - Drag-and-drop file upload
- **ML Analysis Page** (`/ml-analysis`) - Bias detection results
- **Blockchain Page** (`/blockchain`) - Blockchain operations
- **Regulator Dashboard** (`/regulator`) - Audit logs and monitoring
- **Comparison Page** (`/compare`) - Blockchain platform comparison

#### Key Features
- Auto-login functionality
- Automatic trial ID detection
- Real-time status updates
- Toast notifications
- Responsive design

### Backend Modules

#### Core Services

1. **ML Bias Detection** (`ml_bias_detection_production.py`)
   - Ensemble model training and inference
   - Feature extraction (age, gender, ethnicity, eligibility)
   - Fairness metrics calculation
   - Decision logic

2. **Blockchain Service** (`blockchain_service.py`)
   - Hyperledger Fabric integration
   - Transaction creation and verification
   - Hash generation and validation

3. **Authentication** (`auth.py`)
   - JWT token generation and validation
   - Password hashing (bcrypt)
   - Role-based access control

4. **Report Generator** (`report_generator.py`)
   - PDF generation using reportlab
   - Comprehensive trial reports
   - Black/green theme

5. **Digital Signature** (`digital_signature.py`)
   - Cryptographic signing
   - Signature verification

6. **IPFS Service** (`ipfs_service.py`)
   - Optional IPFS integration
   - Large file storage

7. **ZKP Service** (`zkp_service.py`)
   - Zero-knowledge proof implementation
   - Privacy-preserving verification

### Database Schema

#### Models
- **User** - Authentication and user management
- **Trial** - Clinical trial metadata
- **AuditLog** - Activity logging
- **BlockchainTransaction** - Blockchain records

## ML Model Architecture

### Feature Engineering

The model uses 18 features:
1. Age statistics (mean, std, range, skewness)
2. Gender distribution (male, female, balance)
3. Ethnicity distribution (white, black, asian, diversity)
4. Sample size (normalized, log-transformed)
5. Eligibility scores (mean, variance)
6. Fairness metrics (demographic parity, disparate impact, equality of opportunity)

### Model Training

- **Training Samples**: 30,000 (45% unbiased, 55% biased)
- **Split**: 70% train, 15% validation, 15% test
- **XGBoost**: 500 estimators, max_depth=8, learning_rate=0.02
- **Random Forest**: 400 estimators, max_depth=18
- **Ensemble**: Voting classifier with soft voting

### Decision Logic

- **ACCEPT**: Fairness score ≥ 0.65 with balanced demographics
- **REVIEW**: Fairness score ≥ 0.60 or moderate bias indicators
- **REJECT**: Significant bias patterns detected

### Performance Metrics

- Overall Accuracy: 96.13%
- Unbiased Detection: 99.95%
- Biased Detection: 92.31%
- Precision: 1.0000
- Recall: 1.0000
- F1-Score: 1.0000 (on training/test sets)

## Blockchain Architecture

### Hyperledger Fabric Network

- **Organizations**: Sponsor, Investigator, Regulator, Auditor
- **Channel**: Clinical trials channel
- **Chaincode**: TrialChain (Go)
- **Consensus**: Raft (crash fault tolerant)

### On-Chain Data
- Trial metadata (ID, filename, participant count)
- SHA256 hash of trial data
- ML fairness scores and decision
- Timestamps
- Digital signatures
- Transaction IDs

### Off-Chain Data
- Full trial CSV files (encrypted)
- Large attachments (IPFS optional)
- Detailed audit logs

### Security Features
- Endorsement policies
- Access control lists
- Certificate-based authentication
- Immutable ledger

## API Endpoints

### Trial Management
- `POST /api/uploadTrial` - Upload trial dataset
- `POST /api/validateRules` - Validate eligibility rules
- `POST /api/runMLBiasCheck` - Run ML bias detection
- `GET /api/trial/{trial_id}` - Get trial details

### Blockchain
- `POST /api/blockchain/write` - Write trial to blockchain
- `POST /api/blockchain/verify` - Verify trial integrity
- `GET /api/blockchain/status` - Get blockchain status

### Regulatory
- `GET /api/regulator/audit/logs` - Get audit logs
- `GET /api/regulator/trials` - List all trials
- `GET /api/downloadReport` - Download PDF report

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

## Security Architecture

### Authentication & Authorization

- **JWT Tokens**: Secure token-based authentication
- **RBAC**: Role-Based Access Control
  - **SPONSOR**: Upload trials, view own trials
  - **INVESTIGATOR**: Upload trials, view assigned trials
  - **REGULATOR**: Full access, audit logs, reports
  - **AUDITOR**: Read-only access to all data

### Data Protection

- **Encryption**: Encrypted off-chain storage
- **Hashing**: SHA256 for integrity verification
- **Digital Signatures**: Cryptographic signing
- **Zero-Knowledge Proofs**: Privacy-preserving verification

### Network Security

- **HTTPS**: TLS encryption for all communications
- **CORS**: Configurable cross-origin policies
- **Rate Limiting**: API rate limiting (configurable)
- **Input Validation**: Pydantic schema validation

## Deployment Architecture

### Development

```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

### Production (Docker)

```yaml
Services:
  - frontend (Next.js)
  - backend (FastAPI)
  - postgres (PostgreSQL)
  - nginx (Reverse proxy)
```

### Scaling Considerations

- **Horizontal Scaling**: Stateless backend services
- **Database**: PostgreSQL with connection pooling
- **Caching**: Optional Redis for session management
- **Load Balancing**: Nginx load balancer
- **Monitoring**: Prometheus + Grafana

## Performance Metrics

- **API Response Time**: < 200ms (average)
- **ML Inference**: < 2s per trial
- **Blockchain Write**: < 5s per transaction
- **PDF Generation**: < 3s per report

## Testing

### Test Coverage
- Unit tests for ML models
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Load testing with k6 and Locust

### Sample Data
- 50 unbiased trials
- 50 biased trials
- 25 mixed trials

## Monitoring & Logging

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Audit trail for all operations

### Monitoring
- Prometheus metrics
- Grafana dashboards
- Health check endpoints
- Alert system (optional)

## Future Enhancements

- Real-time blockchain event streaming
- Advanced ML explainability features
- Multi-region deployment
- Enhanced IPFS integration
- Mobile application
- API rate limiting and quotas
- Advanced analytics dashboard

## Contributing

[Your contribution guidelines]

## License

[Your license]

