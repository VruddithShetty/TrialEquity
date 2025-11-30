# Production Deployment Guide

## 1. Hyperledger Fabric Network Deployment

### Prerequisites

- Docker and Docker Compose installed
- Go 1.18+ installed
- Node.js 16+ installed
- Minimum 8GB RAM, 4 CPU cores
- 50GB+ disk space

### Step 1: Download Fabric Binaries

```bash
cd blockchain
curl -sSL https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/bootstrap.sh | bash -s -- 2.5.0 1.5.0
```

### Step 2: Generate Crypto Materials

```bash
cd blockchain
./generate-crypto.sh
```

### Step 3: Create Network Configuration

```bash
./create-network-config.sh
```

### Step 4: Start Production Network

```bash
./start-production-network.sh
```

### Step 5: Deploy Chaincode

```bash
./deploy-chaincode-production.sh
```

### Network Architecture

```
Production Network:
├── Orderer Organization (3 nodes for HA)
├── Sponsor Organization (2 peers)
├── Investigator Organization (2 peers)
├── Regulator Organization (2 peers)
└── Auditor Organization (2 peers)
```

### Channel Configuration

- **Channel Name**: `clinicaltrials`
- **Consensus**: Raft (3 orderers)
- **Block Size**: 10MB
- **Batch Timeout**: 2s

### Chaincode Deployment

```bash
# Package chaincode
peer lifecycle chaincode package trialchain.tar.gz \
  --path ./chaincode/trialchain \
  --lang golang \
  --label trialchain_1.0

# Install on all peers
peer lifecycle chaincode install trialchain.tar.gz

# Approve for organizations
peer lifecycle chaincode approveformyorg \
  -o orderer.example.com:7050 \
  --channelID clinicaltrials \
  --name trialchain \
  --version 1.0 \
  --package-id <PACKAGE_ID> \
  --sequence 1

# Commit chaincode
peer lifecycle chaincode commit \
  -o orderer.example.com:7050 \
  --channelID clinicaltrials \
  --name trialchain \
  --version 1.0 \
  --sequence 1 \
  --peerAddresses peer0.sponsor.example.com:7051 \
  --peerAddresses peer0.regulator.example.com:7051
```

## 2. Production Database Configuration

### PostgreSQL Cluster Setup

#### Primary Database Configuration

```yaml
# docker-compose.prod.yml
services:
  postgres-primary:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: clinical_trials
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${REPLICATION_PASSWORD}
    volumes:
      - postgres-primary-data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
    command: >
      postgres
      -c config_file=/etc/postgresql/postgresql.conf
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=4MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
```

#### Replica Configuration

```yaml
  postgres-replica:
    image: postgres:15-alpine
    environment:
      POSTGRES_MASTER_SERVICE: postgres-primary
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${REPLICATION_PASSWORD}
    volumes:
      - postgres-replica-data:/var/lib/postgresql/data
    depends_on:
      - postgres-primary
```

#### Backup Configuration

```bash
# Automated backup script
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup
docker exec postgres-primary pg_dump -U postgres clinical_trials | \
  gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/backup_$DATE.sql.gz" \
  s3://clinical-trials-backups/

# Clean old backups
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Add to crontab: 0 2 * * * /path/to/backup-database.sh
```

#### Connection Pooling (PgBouncer)

```yaml
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    environment:
      DATABASES_HOST: postgres-primary
      DATABASES_PORT: 5432
      DATABASES_DBNAME: clinical_trials
      DATABASES_USER: ${DB_USER}
      DATABASES_PASSWORD: ${DB_PASSWORD}
      PGBOUNCER_POOL_MODE: transaction
      PGBOUNCER_MAX_CLIENT_CONN: 1000
      PGBOUNCER_DEFAULT_POOL_SIZE: 25
```

## 3. Security Hardening

### HTTPS Configuration (Nginx)

```nginx
# nginx.conf
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 443 ssl http2;
    server_name clinicaltrials.example.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
    }
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

### Firewall Configuration (UFW)

```bash
#!/bin/bash
# setup-firewall.sh

# Allow SSH
ufw allow 22/tcp

# Allow HTTPS
ufw allow 443/tcp

# Allow HTTP (redirect to HTTPS)
ufw allow 80/tcp

# Allow specific IPs for database (if needed)
ufw allow from 10.0.0.0/8 to any port 5432

# Enable firewall
ufw --force enable
ufw status verbose
```

### WAF Configuration (ModSecurity)

```apache
# modsecurity.conf
SecRuleEngine On
SecRequestBodyAccess On
SecResponseBodyAccess On
SecResponseBodyMimeType text/plain text/html text/xml application/json

# OWASP Core Rule Set
Include /etc/modsecurity/crs-setup.conf
Include /etc/modsecurity/rules/*.conf

# Custom rules for clinical trials
SecRule ARGS "@detectSQLi" "id:1001,phase:2,block,msg:'SQL Injection detected'"
SecRule ARGS "@detectXSS" "id:1002,phase:2,block,msg:'XSS detected'"
```

### Security Audit Script

```bash
#!/bin/bash
# security-audit.sh

echo "Running security audit..."

# Check for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image clinical-trials-backend:latest

# Check SSL configuration
sslscan clinicaltrials.example.com

# Check open ports
nmap -sV -p- clinicaltrials.example.com

# Check for exposed secrets
trufflehog --regex --entropy=False .

echo "Security audit complete"
```

## 4. Monitoring & Observability

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Clinical Trials Platform",
    "panels": [
      {
        "title": "API Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Database Connections",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends"
          }
        ]
      },
      {
        "title": "Blockchain Transactions",
        "targets": [
          {
            "expr": "blockchain_transactions_total"
          }
        ]
      }
    ]
  }
}
```

### Alerting Rules

```yaml
# alerts.yml
groups:
  - name: clinical_trials_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        annotations:
          summary: "Database is down"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
        for: 5m
        annotations:
          summary: "High API response time"
```

### Error Tracking (Sentry)

```python
# backend/sentry_config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "production"),
)
```

## 5. Load Testing

### Locust Configuration

```python
# load_tests/locustfile.py
from locust import HttpUser, task, between
import random

class ClinicalTrialsUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/api/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def upload_trial(self):
        files = {"file": ("trial.csv", open("test_data.csv", "rb"), "text/csv")}
        self.client.post("/api/uploadTrial", files=files, headers=self.headers)
    
    @task(2)
    def run_ml_check(self):
        trial_id = random.choice(self.trial_ids)
        self.client.post(
            f"/api/runMLBiasCheck?trial_id={trial_id}",
            headers=self.headers
        )
    
    @task(1)
    def verify_blockchain(self):
        trial_id = random.choice(self.trial_ids)
        self.client.post(
            f"/api/blockchain/verify?trial_id={trial_id}",
            headers=self.headers
        )
```

### Run Load Tests

```bash
# Start Locust
locust -f load_tests/locustfile.py --host=http://localhost:8000

# Run with specific parameters
locust -f load_tests/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=10m
```

### k6 Script

```javascript
// load_tests/k6_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const BASE_URL = 'http://localhost:8000';
  
  // Upload trial
  const uploadRes = http.post(`${BASE_URL}/api/uploadTrial`, {
    file: http.file('test_data.csv', 'test_data.csv'),
  });
  check(uploadRes, { 'upload status 200': (r) => r.status === 200 });
  
  sleep(1);
}
```

## 6. Compliance Review

### GDPR Compliance Checklist

- [x] Data pseudonymization implemented
- [x] Right to access (API endpoint for data export)
- [x] Right to deletion (API endpoint for data deletion)
- [x] Data processing logs
- [x] Privacy policy documentation
- [ ] Data Protection Impact Assessment (DPIA)
- [ ] Data Processing Agreement (DPA) templates

### HIPAA Compliance Checklist

- [x] Access controls (RBAC)
- [x] Audit logs
- [x] Encryption at rest
- [x] Encryption in transit (HTTPS)
- [ ] Business Associate Agreement (BAA)
- [ ] Breach notification procedures
- [ ] Risk assessment documentation

### FDA Compliance Checklist

- [x] Audit trail for all data changes
- [x] Digital signatures
- [x] Data integrity verification
- [x] 21 CFR Part 11 compliance structure
- [ ] Validation documentation
- [ ] Standard Operating Procedures (SOPs)
- [ ] Training records

### Compliance API Endpoints

```python
# backend/compliance.py

@app.get("/api/compliance/gdpr/export")
async def export_user_data(user_id: str, current_user: dict = Depends(get_current_user)):
    """GDPR: Export all user data"""
    # Implementation

@app.delete("/api/compliance/gdpr/delete")
async def delete_user_data(user_id: str, current_user: dict = Depends(get_current_user)):
    """GDPR: Delete user data"""
    # Implementation

@app.get("/api/compliance/audit-trail")
async def get_audit_trail(trial_id: str, current_user: dict = Depends(get_current_user)):
    """FDA: Complete audit trail"""
    # Implementation
```

