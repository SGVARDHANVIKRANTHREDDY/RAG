#!/bin/bash
set -e

echo "⚠️  WARNING: This will delete all data!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo "🗑️  Stopping containers..."
docker-compose down -v

echo "🚀 Starting fresh..."
./docker-dev.sh

echo "✅ Database reset complete!"
