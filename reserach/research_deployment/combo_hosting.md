# Combo/Monorepo Hosting

These platforms can host both the frontend and backend on a single service, simplifying deployment.

## Comparison

| Feature | Render (Both) | DigitalOcean App Platform (Both) | Heroku (Both) |
|---------|--------------|----------------------------------|---------------|
| **How it works** | Separate services in same workspace: static site (free) + web service (paid) | Single app with multiple components (static + service) | Two apps or multi-process Procfile |
| **Frontend served by** | Render CDN (static site) | DO CDN (static site component) | Same dyno as backend, or separate app |
| **Backend served by** | Docker container | Docker container | Docker container or buildpack |
| **Single deploy?** | No -- two services, two deploys | Yes -- one `app.yaml` deploys both | Two apps or monorepo via Procfile |
| **Custom domain** | One domain per service (or subdomain routing) | One domain with routing rules | One domain per app |
| **Cost** | Free (static) + $7-25 (backend) = $7-25/mo | $0 (static, DON'T need paid) + $5-25 (backend) = $5-25/mo | $7 (Basic dyno, student credit) |
| **Complexity** | Low -- Render handles both | Low -- single config file | Medium -- heroku.yml + multi-process |

## Detailed Notes

### Render (Frontend + Backend)

Render is designed for this split architecture. You create two services in the same workspace:

1. **Static Site** (free): point it at the `frontend/` directory, set the build command (`npm run build`) and publish directory (`dist/`).
2. **Web Service** (paid): point it at the `backend/` directory with a Dockerfile.

Both auto-deploy from the same GitHub repo (monorepo support is built in -- you specify the root directory for each service).

**Routing:** The frontend runs on `analemma.example.com` and the backend on `api.analemma.example.com` (or a Render subdomain). The frontend makes API calls to the backend URL (configured via environment variable).

**Pros:**
- Clean separation of concerns
- Static site is free
- Both deploy on git push
- Pull request previews for both

**Cons:**
- Two separate services to manage
- CORS must be configured on the backend (FastAPI CORSMiddleware with the frontend origin)
- Two subdomains needed if using custom domain (or use path-based routing which is more complex)

### DigitalOcean App Platform (Both Components)

DO App Platform supports multi-component apps via a single `.do/app.yaml` spec file. You define:

```yaml
name: analemma
services:
  - name: api
    dockerfile_path: backend/Dockerfile
    source_dir: /backend
    http_port: 8000
    instance_size_slug: basic-s
    instance_count: 1
    routes:
      - path: /api
  - name: frontend
    source_dir: /frontend
    build_command: npm run build
    environment_slug: node-js
    routes:
      - path: /
```

A single deploy handles both. The platform routes `/api/*` to the backend and everything else to the frontend CDN.

**Pros:**
- Single deployment configuration
- Path-based routing (no CORS issues! frontend and backend share the same domain)
- Static component is free; only the backend container costs money
- Student credit covers the backend
- DDoS protection, automatic HTTPS

**Cons:**
- DO's framework auto-detection is less polished than Vercel's
- Less developer community than Render for troubleshooting
- 1 GiB bandwidth on free static tier is low (but paid tier gets 50+ GiB)

**The path-based routing advantage:** If the frontend and backend share the same domain (e.g., `analemma.example.com` serves the SPA, and `analemma.example.com/api/process` hits the backend), you don't need CORS at all. This is a genuine simplification.

### Heroku (Both)

Heroku doesn't have a native static site service. Options:

1. **Single app with FastAPI serving static files:** Build the frontend, copy the `dist/` folder into the Docker image, serve it via FastAPI's `StaticFiles` mount. One dyno serves everything.
2. **Two separate Heroku apps:** One for the API, one for the frontend (using a static buildpack).

**Option 1 (recommended for Heroku):**

```python
# In FastAPI app.py
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

Build the frontend, copy `dist/` to `static/` in the Docker image. The API routes (`/api/process`) are handled by FastAPI, everything else falls through to the static file mount.

**Pros:**
- One dyno, one deploy, one domain
- No CORS needed
- Student credit covers it ($13/mo for 24 months)
- 24 months of free hosting is the longest offer

**Cons:**
- 512 MB RAM on Basic dyno -- tight for our backend, now it's also serving static files (marginal extra memory)
- Static files are served by the Python process, not a CDN -- slower for users far from the dyno region
- Single point of failure -- if the API is under load, static file serving slows down too
- More complex Docker setup (multi-stage build for frontend + backend)

## Verdict on Combo Hosting

**Combo hosting is simpler** (fewer moving parts, no CORS) but less optimal (no CDN for static files, shared resources). For a portfolio project with low traffic, the simplicity wins.

**If going combo:** DigitalOcean App Platform is the best option -- path-based routing, CDN for static component, student credit covers the cost.

**If going split:** Vercel (frontend) + DigitalOcean or Fly.io (backend) is the most capable setup. You lose the same-domain simplicity but gain a world-class CDN for the frontend.
