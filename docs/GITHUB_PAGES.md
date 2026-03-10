# GitHub Pages Deployment

## Status
✅ Branch `gh-pages` created with landing page

## Manual Activation Required

To enable GitHub Pages for this repository:

### Step 1: Push to GitHub
```bash
cd /root/.openclaw/workspace/projects/rozlicz
git remote add origin https://github.com/YOUR_USERNAME/rozlicz.git
git push origin main
git push origin gh-pages
```

### Step 2: Enable GitHub Pages
1. Go to repository Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages` / root
4. Click Save

### Step 3: Access Your Site
- URL: `https://YOUR_USERNAME.github.io/rozlicz`
- Or custom domain (see below)

## Custom Domain Setup

### Option 1: rozlicz.pl
1. Purchase domain from current owner or aftermarket
2. Add DNS records:
   - A record: 185.199.108.153
   - A record: 185.199.109.153
   - A record: 185.199.110.153
   - A record: 185.199.111.153
3. Add `CNAME` file with `rozlicz.pl`
4. Enable HTTPS in GitHub Pages settings

### Option 2: rozlicz.ai / rozlicz.io
1. Purchase from Namecheap/Cloudflare/GoDaddy
2. Same DNS setup as above
3. Add `CNAME` file with domain name

## Domain Pricing Research

| Domain | Status | Est. Price | Where to Buy |
|--------|--------|------------|--------------|
| rozlicz.pl | Taken (resale) | $500-3000 | Aftermarket (sedo.com, dan.com) |
| rozlicz.ai | Available | $100-150/year | Namecheap, Cloudflare |
| rozlicz.io | Available | $30-50/year | Namecheap, Cloudflare |
| rozlicz.app | Available | $15-20/year | Google Domains, Cloudflare |

### Recommended Action
1. **For testing**: Use free `github.io` subdomain
2. **For launch**: Buy `rozlicz.io` (~$40) or `rozlicz.app` (~$15)
3. **Later**: Negotiate `rozlicz.pl` if brand gains traction

## Next Steps

1. Create GitHub repository
2. Push both branches
3. Enable Pages in settings
4. (Optional) Connect custom domain
5. Update GA and Meta Pixel IDs in index.html

## Current Branches

- `main` — Full project codebase
- `gh-pages` — Static landing page for GitHub Pages
