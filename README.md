# TrialEquity - Clinical Trial Bias Detection Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18%2B-green)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/docker-enabled-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Production-grade platform for detecting bias in clinical trials using machine learning and blockchain technology**

![Platform Comparison](./docs/screenshots/platform-comparison.png)

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [Development Guide](#development-guide)
- [API Documentation](#api-documentation)
- [Database Setup](#database-setup)
- [Blockchain Setup](#blockchain-setup)
- [ML Model](#ml-model)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Project Overview

**TrialEquity** is an enterprise-grade clinical trial management platform that:

✅ **Detects demographic bias** using an ensemble ML model (96.13% accuracy)  
✅ **Records trials immutably** on Hyperledger Fabric blockchain  
✅ **Ensures regulatory compliance** (HIPAA, FDA 21 CFR Part 11)  
✅ **Provides complete audit trails** for all platform activities  
✅ **Compares blockchain platforms** for optimal trial management  
✅ **Generates compliance reports** in PDF format  

**Status**: ✅ Production-Ready | **Last Updated**: February 2026

---

## ✨ Key Features

### Machine Learning Bias Detection
- **Ensemble Model**: XGBoost + Random Forest (Voting Classifier)
- **Accuracy**: 96.13% (exceeds 95% target)
- **Fairness Metrics**: Demographic Parity, Disparate Impact Ratio, Equality of Opportunity
- **Real-time Analysis**: <2 seconds per trial
- **Explainability**: SHAP/LIME interpretability

### Blockchain Integration
- **Platform**: Hyperledger Fabric 2.x with 4-node consensus
- **Finality**: ~1 second per transaction
- **Security**: Digital signatures, Zero-Knowledge Proofs (ZKP)
- **Storage**: Immutable audit trail + IPFS integration
- **Comparison**: Side-by-side analysis of Hyperledger, MultiChain, Quorum

### Advanced Security
- **Authentication**: JWT token-based with bcrypt hashing
- **Authorization**: Role-Based Access Control (RBAC) - 4 roles
- **Encryption**: AES-256 for sensitive data
- **Audit Logging**: Complete activity tracking with tamper detection

### Regulatory Compliance
- **Standards**: HIPAA-ready, FDA 21 CFR Part 11 compliant
- **Reports**: Automated PDF generation with digital signatures
- **Audit Trails**: Immutable logs for regulatory review
- **Real-time Alerts**: Automatic notification on data anomalies

---

## 💻 Tech Stack

### Frontend
```
Framework:        Next.js 14 (App Router)
Language:         TypeScript
Styling:          Tailwind CSS + ShadCN UI
Animations:       Framer Motion
State Management: React Hooks
HTTP Client:      Axios
Charts:           Recharts
```

### Backend
```
Framework:        FastAPI (Python 3.10+)
ORM:              Motor + Beanie (MongoDB async)
Validation:       Pydantic v2
Authentication:   JWT + bcrypt
Server:           Uvicorn
Database:         MongoDB (async)
```

### Machine Learning
```
Ensemble:         XGBoost + Random Forest
Outlier Detection:Isolation Forest
Scaling:          StandardScaler
Testing:          Chi-square, Kolmogorov-Smirnov
Explainability:   SHAP, LIME
Libraries:        pandas, numpy, scikit-learn>=1.4.0
```

### Blockchain
```
Platform:         Hyperledger Fabric 2.x
Chaincode:        Go
Consensus:        Raft
Nodes:            4 (Sponsor, Investigator, Regulator, Auditor)
```

### DevOps
```
Containerization: Docker & Docker Compose
Reverse Proxy:    Nginx
API Docs:         Swagger/OpenAPI
Monitoring:       Prometheus + Grafana (optional)
```

---

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.15+, Ubuntu 18.04+
- **CPU**: 4 cores (8+ recommended)
- **RAM**: 8GB (16GB+ recommended)
- **Disk**: 20GB free space

### Required Software
- **Node.js**: 18.0 or higher
- **Python**: 3.10 or higher
- **Docker**: 20.10+ (optional but recommended)
- **Docker Compose**: 1.29+ (optional but recommended)
- **MongoDB**: 5.0+ (local or Atlas cloud)
- **Git**: 2.30+

### Optional for Blockchain
- **Docker**: Required for Hyperledger Fabric
- **Go**: 1.16+ (for chaincode development)

---

## 🚀 Quick Start (5 minutes)

### Using Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/clinical-trial-comparer.git
cd clinical-trial-comparer

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be ready (~30 seconds)
docker-compose logs -f

# 4. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup (Development)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/clinical-trial-comparer.git
cd clinical-trial-comparer

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure backend
cat > .env << EOF
MONGODB_URL=mongodb://localhost:27017/clinical_trials
JWT_SECRET=$(openssl rand -hex 32)
ENVIRONMENT=development
EOF

# 4. Start backend (in new terminal)
uvicorn main:app --reload --port 8000

# 5. Setup frontend (in another terminal)
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# 6. Start frontend
npm run dev

# 7. Open browser
# Frontend: http://localhost:3000
```

---

## 📦 Installation

### Prerequisites Installation

#### Windows
```powershell
# Install Node.js
# Download from https://nodejs.org/ (18+ LTS)

# Install Python
# Download from https://www.python.org/ (3.10+)

# Install Docker Desktop
# Download from https://www.docker.com/products/docker-desktop

# Verify installations
node --version      # v18.0.0+
python --version    # Python 3.10+
docker --version    # Docker 20.10+
```

#### macOS
```bash
# Using Homebrew
brew install node@18
brew install python@3.10
brew install docker

# Verify installations
node --version
python3 --version
docker --version
```

#### Ubuntu/Linux
```bash
# Update package manager
sudo apt update

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python
sudo apt install -y python3.10 python3.10-venv

# Install Docker
sudo apt install -y docker.io docker-compose

# Verify installations
node --version
python3 --version
docker --version
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create configuration file
cat > .env << EOF
# Database
MONGODB_URL=mongodb://localhost:27017/clinical_trials

# Authentication
JWT_SECRET=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
EOF

# Verify setup
python -c "import fastapi; print('FastAPI installed successfully')"
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create configuration file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=TrialEquity
NEXT_PUBLIC_ENVIRONMENT=development
EOF

# Verify setup
npm list react next
```

---

## ▶️ Running the Project

### Development Mode

#### Option 1: Using Docker Compose (All-in-One)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Restart services
docker-compose restart backend
```

**Service URLs**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MongoDB: mongodb://localhost:27017

#### Option 2: Terminal Approach (Separate Terminals)

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Terminal 3 - MongoDB** (if running locally):
```bash
# macOS
brew services start mongodb-community

# Windows
mongod

# Linux
sudo systemctl start mongod
```

### Production Mode

```bash
# Using Docker Compose Production Config
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production services
docker-compose -f docker-compose.prod.yml down
```

### Testing Services

Default admin login:
- Email: `user@example.com`
- Password: `password123`

```bash
# Test backend API
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Test frontend
open http://localhost:3000  # macOS
start http://localhost:3000 # Windows
```

---

## 📂 Project Structure

```
clinical-trial-comparer/
│
├── frontend/                          # Next.js Frontend Application
│   ├── app/
│   │   ├── page.tsx                  # Home page
│   │   ├── layout.tsx                # Root layout
│   │   ├── globals.css               # Global styles
│   │   ├── error.tsx                 # Error boundary
│   │   ├── not-found.tsx             # 404 page
│   │   ├── login/
│   │   │   └── page.tsx              # Login page
│   │   ├── upload/
│   │   │   └── page.tsx              # Trial upload page
│   │   ├── ml-analysis/
│   │   │   └── page.tsx              # ML bias analysis page
│   │   ├── blockchain/
│   │   │   └── page.tsx              # Blockchain records page
│   │   ├── compare/
│   │   │   └── page.tsx              # Platform comparison page ⭐
│   │   ├── regulator/
│   │   │   └── page.tsx              # Regulatory dashboard
│   │   ├── admin/
│   │   │   └── page.tsx              # Admin panel
│   │   ├── files/
│   │   │   └── page.tsx              # File management
│   │   └── verify/
│   │       └── page.tsx              # Verification page
│   │
│   ├── components/
│   │   ├── Navigation.tsx             # Main navigation
│   │   ├── RealTimeAlerts.tsx         # Alert notifications
│   │   └── ui/                        # ShadCN UI components
│   │
│   ├── hooks/
│   │   └── use-toast.ts              # Toast notification hook
│   │
│   ├── lib/
│   │   ├── api.ts                    # API client configuration
│   │   ├── utils.ts                  # Utility functions
│   │   └── date-utils.ts             # Date utilities
│   │
│   ├── public/                        # Static assets
│   ├── package.json                  # NPM dependencies
│   ├── tsconfig.json                 # TypeScript config
│   ├── tailwind.config.js            # Tailwind CSS config
│   ├── next.config.js                # Next.js config
│   ├── middleware.ts                 # Next.js middleware
│   └── Dockerfile                    # Docker container config
│
├── backend/                           # FastAPI Backend Application
│   ├── main.py                       # Main app & routes
│   ├── auth.py                       # Authentication logic
│   ├── database.py                   # MongoDB connection
│   ├── models.py                     # MongoDB/Pydantic models
│   ├── schemas.py                    # Request/response schemas
│   │
│   ├── ml_bias_detection_production.py  # ML model (main)
│   ├── blockchain_service.py         # Blockchain operations
│   ├── digital_signature.py          # Signing/verification
│   ├── zkp_service.py                # Zero-knowledge proofs
│   ├── ipfs_service.py               # IPFS integration
│   ├── tokenization_service.py       # Anonymization
│   ├── report_generator.py           # PDF report generation
│   │
│   ├── models/
│   │   ├── xgb_model.pkl             # XGBoost model
│   │   ├── rf_model.pkl              # Random Forest model
│   │   ├── isolation_forest.pkl      # Outlier detection
│   │   ├── scaler.pkl                # Feature scaler
│   │   ├── feature_names.json        # Feature names
│   │   └── model_accuracy.json       # Model metrics
│   │
│   ├── blockchain/
│   │   └── [blockchain chaincode]
│   │
│   ├── scripts/
│   │   ├── check-errors.py           # Error checking
│   │   ├── retrain_ml_model.py       # Model retraining
│   │   ├── start-backend.ps1         # Windows startup
│   │   └── start-server.py           # Server startup
│   │
│   ├── tests/
│   │   ├── test_app_comprehensive.py # Comprehensive tests
│   │   ├── test_all_trials.py        # Trial tests
│   │   ├── test_unbiased_trial.py    # Unbiased trial tests
│   │   └── test_model_with_large_dataset.py
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── requirements-min.txt          # Minimal dependencies
│   ├── .env.example                  # Example env file
│   ├── Dockerfile                    # Docker config
│   └── __pycache__/                  # Python cache
│
├── blockchain/                        # Hyperledger Fabric Setup
│   ├── crypto-config.yaml            # Cryptographic config
│   ├── configtx.yaml                 # Network config
│   ├── setup-network.sh              # Network setup script
│   ├── start-production-network.sh   # Production startup
│   ├── generate-crypto.sh            # Crypto generation
│   ├── deploy-chaincode-production.sh
│   └── chaincode/
│       └── trialchain.go             # Go chaincode
│
├── ml_models/                         # ML Model Training
│   ├── download_clinicaltrials.py    # Data download
│   ├── download_and_categorize_trials.py
│   ├── synthetic_data_generator.py   # Synthetic data
│   └── downloaded_trials/            # Trial data
│
├── trials/                            # Sample Trial Data
│   ├── unbiased_trials/              # 50 unbiased examples
│   ├── biased_trials/                # 50 biased examples
│   └── mixed_trials/                 # 25 borderline cases
│
├── scripts/                           # Utility Scripts
│   ├── start-all.sh                  # Start all services
│   ├── start-all.ps1                 # Windows version
│   ├── START_BACKEND.bat             # Windows backend
│   ├── START_FRONTEND.bat            # Windows frontend
│   ├── backup-database.sh            # Database backup
│   ├── setup-firewall.sh             # Firewall config
│   ├── download_50_trials.sh         # Trial download
│   └── train-production-model.py     # Model training
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md               # System architecture
│   ├── API_DOCUMENTATION.md          # API reference
│   ├── ML_MODELS.md                  # ML model details
│   ├── PRODUCTION_ML_MODEL.md        # Production setup
│   └── screenshots/                  # UI screenshots
│
├── docker-compose.yml                # Development Docker config
├── docker-compose.prod.yml           # Production Docker config
│
├── .gitignore                        # Git ignore rules
├── .env.example                      # Example environment file
├── README.md                         # This file
└── LICENSE                           # MIT License
```

---

## 👨‍💻 Development Guide

### Setting Up IDE (VS Code)

```bash
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.debugpy
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension bradlc.vscode-tailwindcss
code --install-extension tamasfe.even-better-toml
```

### Code Standards

#### Python (Backend)
```bash
# Format code with Black
black backend/

# Lint with Flake8
flake8 backend/

# Type checking with Mypy
mypy backend/

# Sort imports
isort backend/
```

#### TypeScript (Frontend)
```bash
# Format code with Prettier
npm run format

# Lint with ESLint
npm run lint

# Type checking
npx tsc --noEmit
```

### Making Code Changes

#### Backend Changes
```bash
cd backend

# Activate venv
source venv/bin/activate

# Edit files
# Example: backend/main.py

# Test changes
pytest tests/

# Format and lint
black . && flake8 .

# Restart backend
# (if using --reload, automatically detected)
```

#### Frontend Changes
```bash
cd frontend

# Edit files
# Example: frontend/app/compare/page.tsx

# Check for errors
npm run lint

# Format
npm run format

# Hot reload works automatically with npm run dev
```

---

## 📡 API Documentation

### Access API Docs

```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc

# OpenAPI JSON
http://localhost:8000/openapi.json
```

### Key Endpoints

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/auth/login` | POST | User login | ❌ |
| `/api/auth/register` | POST | User registration | ❌ |
| `/api/uploadTrial` | POST | Upload trial data | ✅ |
| `/api/runMLBiasCheck` | POST | Run ML analysis | ✅ |
| `/api/blockchain/write` | POST | Write to blockchain | ✅ |
| `/api/blockchain/verify` | POST | Verify trial | ✅ |
| `/api/compareBlockchains` | GET | Compare platforms | ✅ |
| `/api/downloadReport` | GET | Download report | ✅ |
| `/api/regulator/audit/logs` | GET | View audit logs | ✅ |
| `/api/admin/retrain-model` | POST | Retrain ML model | ✅ Admin |
| `/api/admin/health` | GET | System health | ✅ Admin |

### Example API Calls

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Upload trial
curl -X POST http://localhost:8000/api/uploadTrial \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@trial_data.csv"

# Compare blockchains
curl -X GET http://localhost:8000/api/compareBlockchains \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🗄️ Database Setup

### MongoDB Connection

#### Local MongoDB
```bash
# macOS
brew services start mongodb-community

# Windows (if installed)
mongod

# Linux
sudo systemctl start mongod

# Verify connection
mongo mongodb://localhost:27017/clinical_trials
```

#### MongoDB Atlas (Cloud)
```bash
# 1. Create account at https://www.mongodb.com/cloud/atlas
# 2. Create cluster
# 3. Get connection string
# 4. Update .env:
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/clinical_trials?retryWrites=true&w=majority
```

### Database Initialization

```bash
# The database is automatically created on first connection
# Collections are created as needed by Beanie ORM

# Manual verification
mongo mongodb://localhost:27017/clinical_trials

# View collections
db.getCollectionNames()

# View sample document
db.trials.findOne()
```

### Backup & Restore

```bash
# Backup MongoDB
mongodump --uri="mongodb://localhost:27017/clinical_trials" --out=./backup

# Restore MongoDB
mongorestore --uri="mongodb://localhost:27017/clinical_trials" ./backup/clinical_trials
```

---

## ⛓️ Blockchain Setup

### Hyperledger Fabric Network

```bash
cd blockchain

# Generate cryptographic materials
./generate-crypto.sh

# Setup network
./setup-network.sh

# Start production network
./start-production-network.sh

# Deploy chaincode
./deploy-chaincode-production.sh

# View network status
docker ps | grep hyperledger
```

### Verify Blockchain

```bash
# Check peer logs
docker logs org1.example.com_peer0

# Check orderer logs
docker logs orderer.example.com

# Query chaincode
peer chaincode query -C clinical_trials -n trialchain -c '{"Args":["GetTrial","TRIAL_ID"]}'
```

---

## 🧠 ML Model

### Model Architecture

```python
# Ensemble: XGBoost (66% weight) + Random Forest (33% weight)
# Features: 18 (demographics, fairness metrics, statistical)
# Accuracy: 96.13%
# Decision Output: ACCEPT / REVIEW / REJECT
```

### Model Training

```bash
cd backend/scripts

# Train production model (on 30,000 samples)
python train-production-model.py

# Retrain model
python retrain_ml_model.py

# Check model accuracy
python ../check_trial.py
```

### Model Explanation

```bash
cd backend

# Generate SHAP explanations
python -c "from ml_bias_detection_production import *; explain_prediction(trial_data)"

# View feature importance
python -c "import pickle; m = pickle.load(open('models/xgb_model.pkl', 'rb')); print(m.feature_importances_)"
```

---

## 🧪 Testing

### Run All Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app_comprehensive.py

# Run specific test
pytest tests/test_app_comprehensive.py::test_upload_trial -v

# Run with verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x
```

### Frontend Testing

```bash
cd frontend

# Run linting
npm run lint

# Build check
npm run build

# Run tests (if configured)
npm test
```

### Manual Testing Checklist

- [ ] Login page loads
- [ ] Can create account
- [ ] Token expires properly
- [ ] Can upload trial CSV
- [ ] ML analysis completes
- [ ] Blockchain write succeeds
- [ ] Platform comparison loads
- [ ] Reports download
- [ ] Audit logs display

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build images
docker build -t trialequity-frontend ./frontend
docker build -t trialequity-backend ./backend

# Run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

### Environment Variables for Production

```bash
# backend/.env.prod
MONGODB_URL=mongodb+srv://prod_user:password@prod-cluster.mongodb.net/clinical_trials
JWT_SECRET=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]

# frontend/.env.production.local
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

### Cloud Deployment Options

#### AWS
```bash
# ECS/Fargate deployment
# RDS for MongoDB (or DocumentDB)
# ALB for load balancing
# CloudFront for CDN
```

#### Azure
```bash
# Azure Container Instances
# Azure Cosmos DB (MongoDB API)
# Application Gateway
# Azure CDN
```

#### GCP
```bash
# Cloud Run for containers
# MongoDB Atlas or Firestore
# Cloud Load Balancing
# Cloud CDN
```

---

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### MongoDB Connection Error

```bash
# Check MongoDB is running
mongo --version

# Start MongoDB
# macOS: brew services start mongodb-community
# Windows: mongod
# Linux: sudo systemctl start mongod

# Test connection
mongosh mongodb://localhost:27017/clinical_trials
```

#### API Not Responding

```bash
# Check backend is running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

#### CORS Errors

```bash
# Verify NEXT_PUBLIC_API_URL matches backend port
# Check backend CORS configuration in main.py

# Add to .env
CORS_ORIGINS=["http://localhost:3000"]
```

#### ML Model Not Loading

```bash
# Check model files exist
ls -la backend/models/

# Verify pickle files are valid
python -c "import pickle; pickle.load(open('backend/models/xgb_model.pkl', 'rb'))"

# Retrain model
cd backend/scripts
python retrain_ml_model.py
```

#### Docker Issues

```bash
# Remove all containers
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

### Getting Help

1. **Check logs**: `docker-compose logs -f [service]`
2. **Run tests**: `pytest tests/ -v`
3. **API docs**: http://localhost:8000/docs
4. **GitHub Issues**: Create detailed issue with logs
5. **Email Support**: support@trialequity.com

---

## 🤝 Contributing

### Code Style

- **Python**: PEP 8 with Black formatter
- **TypeScript**: ESLint + Prettier
- **Commits**: Conventional Commits format

### Making Contributions

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# 3. Format code
black . && npm run format

# 4. Run tests
pytest tests/ && npm run lint

# 5. Commit
git add .
git commit -m "feat: add your feature description"

# 6. Push
git push origin feature/your-feature-name

# 7. Create Pull Request
```

### Pull Request Guidelines

- Provide clear description
- Include related issue number
- Add test coverage
- Update documentation
- Ensure CI passes

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Email**: support@trialequity.com
- **Website**: https://trialequity.com

---

## 🎉 Acknowledgments

- Hyperledger Fabric community
- XGBoost & scikit-learn teams
- Next.js & FastAPI communities
- All contributors and testers

---

**Made with ❤️ by the TrialEquity Team**

**Last Updated**: February 2026  
**Status**: Production Ready ✅

---

## Quick Command Reference

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Run tests
pytest tests/

# Format code
black . && npm run format

# API docs
http://localhost:8000/docs

# Frontend
http://localhost:3000

# Backend
http://localhost:8000
```

Enjoy building bias-free clinical trials! 🚀
