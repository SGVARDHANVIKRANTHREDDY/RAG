#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore-db.sh <backup-file>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/*.sql
    exit 1
fi

BACKUP_FILE=$1

echo "⚠️  This will overwrite current database!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo "📥 Restoring from $BACKUP_FILE..."
docker-compose exec -T postgres psql -U postgres chatbot < $BACKUP_FILE

echo "✅ Database restored!"
