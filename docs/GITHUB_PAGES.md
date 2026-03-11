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

| Domain | Status | Est. Price | Where to Buy | Notes |
|--------|--------|------------|--------------|-------|
| **rozlicz.pl** | 🔴 Taken (resale) | $500-3000 | sedo.com, dan.com, after.market | Premium .pl, need negotiation |
| **rozlicz.ai** | 🟢 Available | ~$100-150/year | Namecheap, Cloudflare | AI trend, good for tech brand |
| **rozlicz.io** | 🟢 Available | ~$30-50/year | Namecheap, Cloudflare | Standard tech TLD |
| **rozlicz.app** | 🟢 Available | ~$15-20/year | Google Domains, Cloudflare | Google's app-focused TLD |
| **rozlicz.dev** | 🟢 Available | ~$15-20/year | Google Domains, Cloudflare | Developer-focused |

### Where to Check Availability
- https://www.namecheap.com/domains/
- https://www.cloudflare.com/products/registrar/
- https://domains.google.com/

### My Recommendation
1. **Phase 1 (testing)**: Use free `github.io` subdomain — $0
2. **Phase 2 (launch)**: Buy `rozlicz.io` or `rozlicz.app` — $15-50/year
3. **Phase 3 (growth)**: Negotiate `rozlicz.pl` — $500-1500 one-time

## Next Steps

1. Create GitHub repository
2. Push both branches
3. Enable Pages in settings
4. (Optional) Connect custom domain
5. Update GA and Meta Pixel IDs in index.html

## Current Branches

- `main` — Full project codebase
- `gh-pages` — Static landing page for GitHub Pages
