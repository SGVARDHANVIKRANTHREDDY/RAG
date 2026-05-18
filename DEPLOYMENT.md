# Deployment Guide

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
