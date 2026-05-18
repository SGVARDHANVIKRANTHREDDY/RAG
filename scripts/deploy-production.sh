#!/bin/bash
set -e

echo "🚀 Deploying to Production..."

# Run tests
echo "🧪 Running tests..."
cd chatbot-backend
pytest tests/ -v
cd ..

cd chatbot-frontend
npm run lint
npm run build
cd ..

# Commit and push
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Deploy: $(date +%Y-%m-%d_%H:%M:%S)" || true
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "Next steps:"
echo "1. Monitor Render deployment: https://dashboard.render.com"
echo "2. Monitor Vercel deployment: https://vercel.com/dashboard"
echo "3. Run post-deployment tests"
echo ""
