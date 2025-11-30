#!/bin/bash

# Automated database backup script for production

set -e

BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${RETENTION_DAYS:-30}
DB_NAME="${DB_NAME:-clinical_trials}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-postgres-primary}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup at $(date)"

# Create backup
echo "Creating backup..."
docker exec postgres-primary pg_dump -U "$DB_USER" "$DB_NAME" | \
    gzip > "$BACKUP_DIR/backup_${DATE}.sql.gz"

# Verify backup
if [ -f "$BACKUP_DIR/backup_${DATE}.sql.gz" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/backup_${DATE}.sql.gz" | cut -f1)
    echo "✅ Backup created successfully: backup_${DATE}.sql.gz (Size: $BACKUP_SIZE)"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Upload to S3 (if AWS credentials are configured)
if [ -n "$AWS_S3_BUCKET" ] && command -v aws &> /dev/null; then
    echo "Uploading to S3..."
    aws s3 cp "$BACKUP_DIR/backup_${DATE}.sql.gz" \
        "s3://${AWS_S3_BUCKET}/postgres-backups/" \
        --storage-class STANDARD_IA
    echo "✅ Uploaded to S3"
fi

# Clean old backups
echo "Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Cleanup complete"

echo "Backup process completed at $(date)"

# Send notification (optional)
if [ -n "$NOTIFICATION_WEBHOOK" ]; then
    curl -X POST "$NOTIFICATION_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Database backup completed: backup_${DATE}.sql.gz\"}"
fi

