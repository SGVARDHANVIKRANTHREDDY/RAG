Redeploy backend.

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
