#!/bin/bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/chatbot_backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

echo "📦 Creating database backup..."
docker-compose exec -T postgres pg_dump -U postgres chatbot > $BACKUP_FILE

echo "✅ Backup created: $BACKUP_FILE"
echo "💾 Size: $(du -h $BACKUP_FILE | cut -f1)"
