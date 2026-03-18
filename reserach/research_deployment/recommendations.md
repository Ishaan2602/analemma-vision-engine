# Deployment Recommendations

## Top 4 Deployment Configurations

### Config 1: "Best Student Value" -- DigitalOcean App Platform (both) + Name.com domain

**Setup:** Everything on DigitalOcean App Platform as a multi-component app. Frontend served from CDN, backend from a Docker container. Path-based routing on a single custom domain.

| Component | Service | Cost/month | Who pays |
|-----------|---------|-----------|----------|
| Frontend | DO App Platform static site | $0 | Free tier |
| Backend | DO App Platform, Shared 1 vCPU / 2 GiB | $25 | Student credit ($200) |
| Domain | `analemma.dev` via Name.com | $0 | Student pack (year 1) |
| SSL | Auto (Let's Encrypt) | $0 | Free |
| CI/CD | GitHub auto-deploy | $0 | Free |
| **Total** | | **$25/month** | **$0 out of pocket for 8 months** |

Credit runs out after 8 months. Then: either switch to a cheaper tier ($10/mo, 1 GiB RAM), migrate to Fly.io, or stop hosting.

**Pros:**
- Single platform, single config file, single domain
- No CORS setup -- path-based routing
- 2 GiB RAM is comfortable for the full stack
- Auto-deploy from GitHub
- Student credit covers 8 months

**Cons:**
- Credit expires after 12 months (or runs out after 8 at $25/mo)
- DO's developer experience is less polished than Render or Fly.io
- If you pick the $10/mo tier (1 GiB RAM), it stretches to ~12 months but RAM is tighter

**Stretch option:** Use the $10/mo tier (1 vCPU, 1 GiB RAM) instead. Trim backend deps (drop matplotlib, pandas, plotly from API requirements). This gets you ~12 months on credit. You'll need to run a single Uvicorn worker and handle one request at a time, which is fine for low traffic.

---

### Config 2: "Best Performance Split" -- Vercel (frontend) + DigitalOcean (backend) + Name.com domain

**Setup:** Frontend on Vercel's free tier for world-class CDN and instant deploys. Backend on DigitalOcean App Platform using student credit. Two subdomains: `analemma.dev` for frontend, `api.analemma.dev` for backend.

| Component | Service | Cost/month | Who pays |
|-----------|---------|-----------|----------|
| Frontend | Vercel free tier | $0 | Free forever |
| Backend | DO App Platform, Shared 1 vCPU / 2 GiB | $25 | Student credit ($200) |
| Domain | `analemma.dev` via Name.com | $0 | Student pack (year 1) |
| SSL | Auto (both platforms) | $0 | Free |
| CI/CD | Vercel auto-deploy + GitHub Actions for backend | $0 | Free |
| **Total** | | **$25/month** | **$0 out of pocket for 8 months** |

**Pros:**
- Frontend on the best possible CDN (Vercel's edge network)
- Preview deployments for frontend PRs
- Backend on a comfortable 2 GiB tier
- Frontend hosting remains free forever even after DO credit runs out

**Cons:**
- Two platforms to manage
- CORS configuration needed on FastAPI backend
- Two subdomains (minor complexity)

**Migration path when DO credit runs out:** Switch backend to Fly.io ($5.70-10.70/mo) or Render Starter ($7/mo). Frontend on Vercel stays free.

---

### Config 3: "Maximum Longevity" -- Heroku (backend, static frontend bundled) + Namecheap domain

**Setup:** Single Heroku app running both FastAPI and serving static frontend files. Basic dyno covered by student credit for 24 months.

| Component | Service | Cost/month | Who pays |
|-----------|---------|-----------|----------|
| Frontend + Backend | Heroku Basic dyno (Docker) | $7 | Student credit ($13/mo) |
| Domain | `analemma.me` via Namecheap | $0 | Student pack (year 1) |
| SSL | Heroku auto-cert | $0 | Free |
| CI/CD | GitHub integration or Actions | $0 | Free |
| Unused credit | $6/mo leftover | -- | -- |
| **Total** | | **$7/month** | **$0 out of pocket for 24 months** |

**Pros:**
- 24 months of free hosting -- the longest of any option
- Single deployment, no CORS
- $6/mo leftover credit could cover a Heroku Postgres if you ever add one
- Heroku's developer experience is mature and well-documented

**Cons:**
- 512 MB RAM is tight. Will need aggressive dep trimming and single-worker mode.
- No CDN for static files -- served by the Python process in the same dyno
- Heroku's Basic dyno CPU is shared and slow for our computation
- Docker deployment via Heroku container registry is less streamlined than Render/Fly
- If you need more RAM, Standard-2X ($50/mo) is $37 out of pocket per month
- Static file serving will be slow for users far from the dyno region

**Feasibility note:** 512 MB is the biggest risk here. You'd need to:
1. Drop matplotlib, pandas, plotly from the API requirements
2. Run only 1 Uvicorn worker
3. Use `--limit-max-requests` to restart workers periodically and prevent memory leaks
4. Pre-download the JPL ephemeris in the Docker build
5. Accept that large image uploads might OOM

This config works for a demo/portfolio but won't handle "real" usage well.

---

### Config 4: "Best DX, Pay-as-You-Go" -- Vercel (frontend) + Fly.io (backend) + Name.com domain

**Setup:** Frontend on Vercel (free forever). Backend on Fly.io with auto-stop to minimize costs. Perfect for a project that gets occasional traffic.

| Component | Service | Cost/month | Who pays |
|-----------|---------|-----------|----------|
| Frontend | Vercel free tier | $0 | Free forever |
| Backend | Fly.io shared-cpu-1x, 2 GB RAM, auto-stop | $2-11 (usage-based) | Out of pocket |
| Domain | `analemma.dev` via Name.com | $0 | Student pack (year 1) |
| SSL | Auto (both platforms) | $0 | Free |
| Dedicated IPv4 | Fly.io shared IPv4 | $0 | Free |
| CI/CD | Vercel auto-deploy + flyctl GitHub Action | $0 | Free |
| **Total** | | **$2-11/month** | **$2-11 out of pocket** |

If traffic is sporadic (portfolio project visited a few times a week), auto-stop keeps the machine off most of the time. Realistic monthly bill: $2-5.

**Pros:**
- Best Docker experience (Fly.io is Docker-native)
- Auto-stop means near-zero cost during quiet periods
- 2 GB RAM is comfortable
- Fly.io can deploy in 30+ regions (pick one close to target audience)
- Frontend on Vercel is best-in-class
- No student credit dependency -- sustainable indefinitely

**Cons:**
- Cold start when machine auto-starts: 15-30 seconds for users hitting a sleeping machine
- Fly.io requires credit card regardless of plan
- Monthly cost is small but not $0
- Two platforms to manage

---

## Decision Matrix

| Criterion | Config 1 (DO Both) | Config 2 (Vercel + DO) | Config 3 (Heroku All) | Config 4 (Vercel + Fly.io) |
|-----------|-------------------|----------------------|---------------------|--------------------------|
| **Monthly cost** | $25 (credit) | $25 (credit) | $7 (credit) | $2-11 (pocket) |
| **Free duration** | 8-12 months | 8-12 months | 24 months | Never free, but cheap |
| **RAM comfort** | 2 GiB (good) | 2 GiB (good) | 512 MB (risky) | 2 GB (good) |
| **Frontend performance** | Good (CDN) | Excellent (Vercel) | Poor (no CDN) | Excellent (Vercel) |
| **Cold start** | None | None | None (Basic dyno) | 15-30s (auto-stop) |
| **Setup complexity** | Low | Medium (CORS) | Medium (Docker + static) | Medium (CORS) |
| **CORS needed?** | No | Yes | No | Yes |
| **Long-term sustainability** | Switch after credit | Switch backend after credit | 24 months then switch | Indefinite at $2-11/mo |
| **Custom domain** | Clean (single domain) | Two subdomains | Single domain | Two subdomains |
| **Developer experience** | Good | Best | Okay | Very good |

## Final Recommendation

**Start with Config 2: Vercel (frontend) + DigitalOcean App Platform (backend).** Then evolve:

### Phase 1 -- Development & Launch (months 1-8)
- Frontend on **Vercel** (free tier, auto-deploy, preview PRs)
- Backend on **DigitalOcean App Platform** ($25/mo, 2 GiB RAM, covered by $200 student credit)
- Domain: **`analemma.dev`** from Name.com (free for 1 year)
- CI/CD: Vercel handles frontend; GitHub Actions deploys backend to DO
- Cost: **$0/month**

### Phase 2 -- Credit Running Low (months 8-12)
- Downgrade DO backend to $10/mo (1 GiB RAM) to stretch credit
- Or switch backend to **Fly.io** ($5.70-10.70/mo, auto-stop for lower costs)
- Frontend stays on Vercel (free forever)
- Cost: **$0-11/month**

### Phase 3 -- After Student Credit (month 12+)
- If project is still active: keep backend on Fly.io ($5-11/mo) or Railway ($5-10/mo)
- If project is dormant: keep frontend on Vercel (free), shut down backend
- Renew domain ($15-20/year) or let it go and use `your-project.vercel.app`
- Cost: **$0-11/month**

### Why Not Config 3 (Heroku)?
Despite the 24-month credit, 512 MB RAM is genuinely risky for our stack. If the backend fails under load or OOMs during a demo, the longevity doesn't help. It's better to have a working app for 8 months than a brittle one for 24.

### Why Not Config 1 (DO Both)?
Config 1 is simpler (no CORS, single domain), and it's a perfectly valid choice. The reason Config 2 edges it out: Vercel's frontend DX is clearly better (instant preview deploys, zero-config framework detection, faster builds), and the frontend will outlive the DO credit. When the credit runs out, you only need to migrate the backend -- the frontend just keeps working.

### What About Config 4 (Vercel + Fly.io)?
Config 4 is the best long-term option and the most cost-efficient for an indefinite timeline. The only downside is cold starts from auto-stop. If you don't have student credits (or after they expire), this is where you should end up. Starting here from day one is also reasonable if you want to avoid any platform migration later.

## Quick-Start Checklist

1. Claim **Name.com** free `.dev` domain from student pack
2. Claim **DigitalOcean** $200 student credit
3. Set up monorepo: `frontend/` + `backend/` + `.github/workflows/`
4. Deploy frontend to **Vercel** (connect GitHub repo, set root to `frontend/`)
5. Deploy backend to **DO App Platform** (Dockerfile in `backend/`, 1 vCPU / 2 GiB)
6. Configure DNS: `analemma.dev` -> Vercel, `api.analemma.dev` -> DO
7. Add CORS middleware to FastAPI allowing `https://analemma.dev`
8. Set `VITE_API_URL=https://api.analemma.dev` in frontend env
9. Test end-to-end
10. Set up GitHub Actions for backend deployment automation
