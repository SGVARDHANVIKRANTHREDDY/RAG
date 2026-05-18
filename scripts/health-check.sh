#!/bin/bash

echo "🏥 Health Check"
echo "==============="
echo ""

# Check backend
echo -n "Backend API: "
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ Healthy"
else
    echo "❌ Down"
fi

# Check frontend
echo -n "Frontend: "
if curl -f -s http://localhost:3000 > /dev/null; then
    echo "✅ Healthy"
else
    echo "❌ Down"
fi

# Check database
echo -n "Database: "
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Down"
fi

echo ""
echo "📊 Container Status:"
docker-compose ps
