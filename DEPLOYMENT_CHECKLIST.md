# Production Deployment Checklist

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
