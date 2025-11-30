# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)
- Hyperledger Fabric prerequisites (for blockchain setup)

## Quick Start with Docker

### 1. Clone Repository

```bash
git clone <repository-url>
cd Clinical_trial_comparer
```

### 2. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- FastAPI backend
- Next.js frontend
- Redis cache
- IPFS (optional)

### 3. Initialize Database

```bash
docker-compose exec backend python -c "from database import init_db; init_db()"
```

### 4. Access Services

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Blockchain Setup

### Hyperledger Fabric

1. Navigate to blockchain directory:
```bash
cd blockchain
```

2. Make setup script executable:
```bash
chmod +x setup-network.sh
```

3. Run setup:
```bash
./setup-network.sh
```

Note: This requires Fabric binaries. For production, follow official Fabric documentation.

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/clinical_trials
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-change-in-production
BLOCKCHAIN_NETWORK=fabric
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### 1. Build Images

```bash
docker-compose build
```

### 2. Set Production Environment Variables

Update `docker-compose.yml` with production values.

### 3. Deploy

```bash
docker-compose up -d
```

### 4. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

## Kubernetes Deployment (Optional)

Kubernetes manifests are available in `k8s/` directory:

```bash
kubectl apply -f k8s/
```

## Monitoring

- Health check: `GET /health`
- Metrics: Available via Prometheus (if configured)
- Logs: `docker-compose logs -f`

## Backup

### Database Backup

```bash
docker-compose exec postgres pg_dump -U postgres clinical_trials > backup.sql
```

### Restore

```bash
docker-compose exec -T postgres psql -U postgres clinical_trials < backup.sql
```

## Troubleshooting

### Port Conflicts

If ports are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Change frontend port
  - "8001:8000"  # Change backend port
```

### Database Connection Issues

Check database is running:
```bash
docker-compose ps postgres
```

### Blockchain Network Issues

Ensure Fabric network is properly configured:
```bash
cd blockchain
./network.sh down  # Clean up
./setup-network.sh  # Recreate
```

## Security Checklist

- [ ] Change default database passwords
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Configure firewall rules
- [ ] Set up proper RBAC
- [ ] Enable audit logging
- [ ] Regular security updates

