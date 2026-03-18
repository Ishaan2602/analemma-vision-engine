# Frontend Hosting Comparison

All of these platforms serve static files (HTML, CSS, JS) from a CDN with HTTPS. The frontend is a Svelte or Vue SPA built to static assets -- a few MB total.

## Comparison Table

| Feature | Vercel (Free) | Netlify (Free) | GitHub Pages | Render (Static) | DO App Platform (Static) |
|---------|--------------|----------------|--------------|-----------------|--------------------------|
| **Cost** | $0 | $0 | $0 | $0 | $0 (free tier: 3 static apps) |
| **Bandwidth** | 100 GB/month | 300 credits/month (~30 GB) | 100 GB/month (soft limit) | 100 GB/month (shared with all services) | 1 GiB/app for free tier |
| **Build minutes** | Unlimited deploys | 300 credits (~20 deploys) | GitHub Actions (2000 min/month free) | 500 min/month | Built-in (from GitHub/GitLab) |
| **Custom domain** | Yes, free | Yes, free | Yes, free | Yes, free | Yes, free |
| **HTTPS/SSL** | Auto (Let's Encrypt) | Auto (Let's Encrypt) | Auto (Let's Encrypt) | Auto (Let's Encrypt) | Auto (Let's Encrypt) |
| **CDN** | Global edge network | Global CDN | Fastly CDN | Cloudflare CDN | CDN included |
| **Deploy from Git** | GitHub, GitLab, Bitbucket | GitHub, GitLab, Bitbucket | GitHub only | GitHub, GitLab, Bitbucket | GitHub, GitLab |
| **Preview deploys** | Yes (per PR) | Yes (per PR) | No (manual) | Yes (per PR) | Yes |
| **SPA routing** | Auto-detected for SvelteKit/Vite | Requires `_redirects` file | Requires 404.html hack | Requires rewrite rules | Supported |
| **Build config** | Auto-detects framework | Auto-detects framework | Needs GitHub Actions workflow | Auto or Docker | Buildpack or Dockerfile |

## Detailed Notes

### Vercel (Free Hobby tier)

The best free static hosting option for a JS framework SPA.

**Pros:**
- Zero-config deployment for Svelte/SvelteKit and Vue/Nuxt -- auto-detects framework and build commands
- Instant preview deployments on every PR
- 100 GB bandwidth is more than enough
- Global edge network with excellent performance
- Unlimited deployments
- Instant rollback
- Built-in web analytics (50k events/month)

**Cons:**
- Hobby plan limited to 1 developer seat
- No commercial use on free tier (technically -- portfolio/educational project is fine)
- Vercel Functions have limits (4 hrs active CPU/month) but we're not using serverless functions

**SPA routing:** Vercel auto-detects SvelteKit/Vite projects and configures routing correctly. For a plain Vite SPA, add a `vercel.json` with a rewrite rule.

**Custom domain:** Add via dashboard, configure DNS with CNAME to `cname.vercel-dns.com`. Works with Namecheap/Name.com.

### Netlify (Free tier)

Very similar to Vercel for static hosting. Slightly more complex with their new credit-based pricing.

**Pros:**
- Auto-detects framework and builds
- Deploy Previews for PRs
- Built-in form handling (1 credit per submission, if needed)
- Functions support (for serverless, if needed)
- Good plugin ecosystem

**Cons:**
- Credit-based pricing is confusing: 300 credits/month on free tier. Each production deploy costs 15 credits, bandwidth costs 10 credits/GB. So ~20 deploys or ~30 GB bandwidth per month.
- Credit limits could be surprising if you deploy frequently during development
- If you exhaust credits, site stays up but new deploys and some features stop until next month

**SPA routing:** Add a `_redirects` file to the build output: `/* /index.html 200`

**Custom domain:** Add via dashboard, configure DNS CNAME. Supports both apex and subdomains.

### GitHub Pages (Free)

Simplest option -- no separate service account needed. Static files served directly from a GitHub repo.

**Pros:**
- Completely free, forever
- No separate account needed
- Custom domains supported with HTTPS
- CI/CD via GitHub Actions (can build Svelte/Vue there)
- 100 GB/month soft bandwidth limit
- Extremely reliable

**Cons:**
- No auto-detected framework builds -- you must write your own GitHub Actions workflow to build the SPA and push to `gh-pages` branch
- No preview deployments per PR (without extra tooling)
- SPA routing hack: must create a `404.html` that redirects to `index.html`, which is clunky
- No server-side features whatsoever
- Files must be in a public repo (or GitHub Pro, which students have)
- 10 deploys per hour limit from GitHub Actions
- Build artifact size limit: 1 GB per repo

**SPA routing:** The 404.html hack works but isn't great. If using hash-based routing (`/#/route`) instead of HTML5 history mode, it's a non-issue.

**Custom domain:** Add a `CNAME` file to the repo root with your domain. Configure DNS CNAME/A records per GitHub docs.

### Render (Static Sites)

Render serves static sites for free alongside their paid backend services.

**Pros:**
- Free static hosting counts against the same 100 GB bandwidth as other services
- Auto-deploys from GitHub/GitLab
- Custom domains with managed TLS
- Pull request previews
- Same platform as the backend (if using Render for backend), which simplifies DNS and management

**Cons:**
- Shares build pipeline minutes (500/month) with backend services
- No edge CDN as fast as Vercel/Netlify's dedicated networks
- Less framework auto-detection polish than Vercel

**Best if:** you're already using Render for the backend and want everything on one platform.

### DigitalOcean App Platform (Static -- Free Tier)

DO's free tier includes 3 static site apps with deployment from Git.

**Pros:**
- Free, with automatic HTTPS and custom domains
- Global CDN with DDoS mitigation
- Deploy from GitHub/GitLab
- Good if you're already using DO for the backend (use student credit for the backend, free tier for static)

**Cons:**
- Only 1 GiB data transfer per free static app (extremely low)
- Less JS framework polish than Vercel/Netlify
- Fewer developer features (no preview environments on free tier)

**Best if:** you're already using DigitalOcean for the backend with student credits.

## Recommendation for Frontend

**Use Vercel (free tier)** for the frontend. It's the most polished option for SPA deployment:
- Zero-config for Svelte and Vue
- Best preview deployment experience
- Most generous bandwidth (100 GB)
- No confusing credit math

GitHub Pages is the runner-up -- completely free with no credit limits -- but requires more manual setup (GitHub Actions workflow, 404.html SPA hack).

Netlify's credit system makes it less predictable than Vercel for frequent deployers during active development.
