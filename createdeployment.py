import os
from pathlib import Path

def create_file(path, content=" "):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def create_docker_deployment():
    pass

def create_render_deployment():
    pass



def create_render_deployment():
    files = {
        "DEPLOY_VERCEL.md": """Redeploy backend.

## Custom Domain

1. Vercel Dashboard → Project → Settings → Domains
2. Add your domain
3. Update DNS records (Vercel provides instructions)

## Preview Deployments

Every Git push creates a preview deployment at:
`https://your-app-git-branch.vercel.app`

## Troubleshooting

### API Calls Failing
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify CORS settings on backend
- Check browser console for errors

### Authentication Issues
- Verify `NEXTAUTH_SECRET` is set
- Check `NEXTAUTH_URL` matches deployment URL

### Build Failures
- Check `npm run build` works locally
- Verify all dependencies in package.json
- Check Node.js version compatibility
""",

        # GitHub Actions CI/CD
        ".github/workflows/deploy.yml": """name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./chatbot-backend
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      
      - name: Run tests
        working-directory: ./chatbot-backend
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/test_db
          JWT_SECRET: test-secret-key-for-ci
        run: pytest tests/ -v

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        working-directory: ./chatbot-frontend
        run: npm ci
      
      - name: Run linter
        working-directory: ./chatbot-frontend
        run: npm run lint
      
      - name: Build
        working-directory: ./chatbot-frontend
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: https://api.example.com/api/v1

  deploy:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render (Backend)
        run: echo "Backend auto-deploys via Render GitHub integration"
      
      - name: Deploy to Vercel (Frontend)
        run: echo "Frontend auto-deploys via Vercel GitHub integration"
""",

        # Deployment checklist
        "DEPLOYMENT_CHECKLIST.md": """# Production Deployment Checklist

## Pre-Deployment

### Backend
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] CORS origins set correctly
- [ ] JWT secret is strong (32+ chars)
- [ ] OpenAI API key configured
- [ ] File upload limits set
- [ ] Error logging configured

### Frontend
- [ ] Build succeeds locally (`npm run build`)
- [ ] Environment variables set
- [ ] API URL points to production backend
- [ ] NextAuth configured
- [ ] Dark mode works
- [ ] Voice input tested (HTTPS required)

### Database
- [ ] PostgreSQL provisioned
- [ ] Connection string obtained
- [ ] Migrations run
- [ ] Backup strategy in place

## Deployment Steps

### 1. Backend (Render)
```bash
# Push to GitHub
git push origin main

# Render auto-deploys from GitHub
# Wait for build to complete

# Initialize database
# (Use Render shell or connect remotely)
python -m app.db.init_db

# Verify health endpoint
curl https://your-backend.onrender.com/health
```

### 2. Frontend (Vercel)
```bash
# Push to GitHub
git push origin main

# Vercel auto-deploys
# Wait for deployment

# Test deployment
# Visit https://your-app.vercel.app
```

### 3. Post-Deployment Tests
- [ ] Can register new user
- [ ] Can login
- [ ] Can create new chat
- [ ] Can upload PDF/DOCX/TXT
- [ ] Can query documents
- [ ] Streaming responses work
- [ ] Voice input works (Chrome/Edge)
- [ ] Dark mode toggle works
- [ ] Chat history persists
- [ ] Logout works

## Monitoring

### Backend (Render)
- Health: `https://your-backend.onrender.com/health`
- API Docs: `https://your-backend.onrender.com/docs`
- Logs: Render Dashboard → Logs

### Frontend (Vercel)
- App: `https://your-app.vercel.app`
- Analytics: Vercel Dashboard → Analytics
- Logs: Vercel Dashboard → Deployments → Logs

## Rollback Plan

### Backend
1. Render Dashboard → Deployments
2. Select previous working deployment
3. Click "Redeploy"

### Frontend
1. Vercel Dashboard → Deployments
2. Find previous deployment
3. Click "Promote to Production"

## Security

- [ ] HTTPS enabled on both services
- [ ] Environment variables not in code
- [ ] Database credentials secure
- [ ] JWT secret not exposed
- [ ] CORS restricted to frontend domain
- [ ] File upload size limits enforced
- [ ] Rate limiting considered

## Performance

- [ ] Database indexes created
- [ ] Static assets cached
- [ ] CDN enabled (Vercel provides)
- [ ] Compression enabled
- [ ] Image optimization (if using images)

## Backup

- [ ] Database backup configured
- [ ] User uploads backed up
- [ ] Environment variables documented
- [ ] Deployment configs in Git
""",
    }
    
    for filepath, content in files.items():
        create_file(filepath, content)
    
    print("\n✅ Render/Vercel deployment files created!")

def create_helper_scripts():
    """Create helper scripts for common tasks"""
    
    files = {
        # Database reset script
        "scripts/reset-db.sh": """#!/bin/bash
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
""",

        # Backup script
        "scripts/backup-db.sh": """#!/bin/bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/chatbot_backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

echo "📦 Creating database backup..."
docker-compose exec -T postgres pg_dump -U postgres chatbot > $BACKUP_FILE

echo "✅ Backup created: $BACKUP_FILE"
echo "💾 Size: $(du -h $BACKUP_FILE | cut -f1)"
""",

        # Restore script
        "scripts/restore-db.sh": """#!/bin/bash
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
""",

        # Production deploy script
        "scripts/deploy-production.sh": """#!/bin/bash
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
""",

        # Log viewer script
        "scripts/view-logs.sh": """#!/bin/bash

echo "📋 Container Logs"
echo "=================="
echo ""
echo "1. All logs"
echo "2. Backend only"
echo "3. Frontend only"
echo "4. Database only"
echo ""
read -p "Select option: " option

case $option in
    1)
        docker-compose logs -f
        ;;
    2)
        docker-compose logs -f backend
        ;;
    3)
        docker-compose logs -f frontend
        ;;
    4)
        docker-compose logs -f postgres
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
""",

        # Health check script
        "scripts/health-check.sh": """#!/bin/bash

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
""",

        # Environment setup script
        "scripts/setup-env.sh": """#!/bin/bash
set -e

echo "🔧 Environment Setup Wizard"
echo "============================"
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists"
    read -p "Overwrite? (yes/no): " overwrite
    if [ "$overwrite" != "yes" ]; then
        exit 0
    fi
fi

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Get OpenAI key
read -p "Enter OpenAI API key (or press Enter to skip): " OPENAI_KEY
if [ -z "$OPENAI_KEY" ]; then
    OPENAI_KEY="sk-your-key-here"
fi

# Generate NextAuth secret
NEXTAUTH_SECRET=$(openssl rand -hex 32)

# Create .env
cat > .env << EOF
# Backend
JWT_SECRET=$JWT_SECRET
OPENAI_API_KEY=$OPENAI_KEY
LLM_MODEL=gpt-4o-mini

# Frontend
NEXTAUTH_SECRET=$NEXTAUTH_SECRET
EOF

echo ""
echo "✅ .env file created!"
echo ""
echo "📝 Please review and edit .env if needed"
echo ""
""",
    }
    
    for filepath, content in files.items():
        create_file(filepath, content)
        # Make scripts executable
        if filepath.endswith('.sh'):
            os.chmod(filepath, 0o755)
    
    print("\n✅ Helper scripts created!")

def create_deployment_readme():
    """Create comprehensive deployment README"""
    
    content = """# Deployment Guide

Complete guide for deploying the Multi-User RAG Chatbot.

## Quick Start (Local Development)

### Using Docker (Recommended)

```bash
# 1. Setup environment
./scripts/setup-env.sh

# 2. Start all services
./docker-dev.sh

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Manual Setup

See individual README files:
- Backend: `chatbot-backend/README.md`
- Frontend: `chatbot-frontend/README.md`

## Production Deployment

### Option 1: Render + Vercel (Recommended)

**Cost**: Free tier available, ~$7/month for production

1. **Backend on Render**
   - See `DEPLOY_RENDER.md`
   - Includes PostgreSQL database
   - Auto-scales based on traffic

2. **Frontend on Vercel**
   - See `DEPLOY_VERCEL.md`
   - Global CDN
   - Automatic previews for PRs

### Option 2: Docker Compose (VPS)

Deploy to any VPS (DigitalOcean, AWS, etc.):

```bash
# 1. Clone repo on server
git clone <your-repo>
cd chatbot

# 2. Setup production environment
cp .env.docker .env.production
# Edit with production values

# 3. Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Kubernetes

For high-scale deployments:
- See `k8s/` directory (if added)
- Supports auto-scaling
- Multi-region deployment

## Deployment Checklist

Before going live, check:

- [ ] All tests passing
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] CORS configured
- [ ] Database backed up
- [ ] Monitoring configured
- [ ] Error tracking (Sentry)
- [ ] Rate limiting enabled

See `DEPLOYMENT_CHECKLIST.md` for complete list.

## Maintenance

### Backups

```bash
# Backup database
./scripts/backup-db.sh

# Restore database
./scripts/restore-db.sh ./backups/chatbot_backup_20260513.sql
```

### Logs

```bash
# View logs
./scripts/view-logs.sh

# Production logs
# Render: Dashboard → Logs
# Vercel: Dashboard → Deployments → Logs
```

### Health Checks

```bash
# Local
./scripts/health-check.sh

# Production
curl https://your-backend.onrender.com/health
```

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Check DATABASE_URL format
- Verify PostgreSQL is running
- Check firewall rules

**CORS Errors**
- Update CORS_ORIGINS on backend
- Include all frontend domains

**File Upload Failing**
- Check file size limits
- Verify storage permissions
- Check MIME type validation

**Streaming Not Working**
- Requires SSE support
- Check NGINX config (if using)
- Verify API URL is correct

### Getting Help

- Check GitHub issues
- Review API logs
- Test with curl/Postman
- Enable debug logging

## Monitoring

### Recommended Tools

- **Uptime**: UptimeRobot (free)
- **Errors**: Sentry (free tier)
- **Analytics**: Vercel Analytics
- **Logs**: Render logs / CloudWatch

### Metrics to Track

- API response times
- Database query performance
- Error rates
- User signup/login rates
- Document upload success rate
- RAG query latency

## Scaling

### Performance Optimization

1. **Database**
   - Add indexes
   - Connection pooling
   - Read replicas

2. **Backend**
   - Increase workers (Gunicorn)
   - Add caching (Redis)
   - CDN for uploads

3. **Frontend**
   - Image optimization
   - Code splitting
   - Static generation

### Horizontal Scaling

- Load balancer (NGINX)
- Multiple backend instances
- Managed database (RDS/Neon)

## Security

### Production Security Checklist

- [ ] HTTPS everywhere
- [ ] Strong JWT secret
- [ ] Password hashing (bcrypt)
- [ ] SQL injection prevention (ORM)
- [ ] XSS protection
- [ ] CSRF tokens
- [ ] Rate limiting
- [ ] Input validation
- [ ] File type validation
- [ ] Secrets in env vars (not code)

### Regular Security Tasks

- Update dependencies monthly
- Review access logs
- Rotate secrets quarterly
- Penetration testing

## Cost Optimization

### Free Tier Limits

**Render**
- 750 hours/month free
- Sleeps after 15min inactivity
- 512MB RAM

**Vercel**
- Unlimited deployments
- 100GB bandwidth
- 6000 build minutes/month

### Upgrade Path

- Render Starter: $7/month (always-on)
- Vercel Pro: $20/month (team features)
- Database: $7-25/month (managed PostgreSQL)

Total: ~$15-30/month for production

## License

MIT
"""
    
    create_file("DEPLOYMENT.md", content)
    print("\n✅ Deployment README created!")

# Main execution
if __name__ == "__main__":
    print("🚀 Creating deployment configuration...\n")
    
    create_docker_deployment()
    create_render_deployment()
    create_helper_scripts()
    create_deployment_readme()
    
    print("\n" + "="*60)
    print("✅ DEPLOYMENT PACKAGE CREATED!")
    print("="*60)
    print("\n📦 Created Files:")
    print("  ├── docker-compose.yml          (Local development)")
    print("  ├── docker-compose.prod.yml     (Production)")
    print("  ├── .env.docker                 (Environment template)")
    print("  ├── docker-dev.sh               (Quick start script)")
    print("  ├── render.yaml                 (Render.com config)")
    print("  ├── DEPLOY_RENDER.md")
    print("  ├── DEPLOY_VERCEL.md")
    print("  ├── DEPLOYMENT_CHECKLIST.md")
    print("  ├── .github/workflows/deploy.yml (CI/CD)")
    print("  └── scripts/")
    print("      ├── setup-env.sh")
    print("      ├── backup-db.sh")
    print("      ├── restore-db.sh")
    print("      ├── deploy-production.sh")
    print("      ├── view-logs.sh")
    print("      └── health-check.sh")
    print("\n🎯 Quick Start:")
    print("  # Local Development (Docker)")
    print("  1. ./scripts/setup-env.sh")
    print("  2. ./docker-dev.sh")
    print("  3. Visit http://localhost:3000")
    print("\n  # Production Deployment")
    print("  1. Read DEPLOY_RENDER.md")
    print("  2. Read DEPLOY_VERCEL.md")
    print("  3. Follow DEPLOYMENT_CHECKLIST.md")
    print("\n📚 Documentation:")
    print("  - DEPLOYMENT.md - Complete guide")
    print("  - DEPLOY_RENDER.md - Backend deployment")
    print("  - DEPLOY_VERCEL.md - Frontend deployment")
    print("="*60)


