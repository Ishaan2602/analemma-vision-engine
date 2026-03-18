# CI/CD, Repo Structure, and Custom Domains

## Monorepo vs Separate Repos

### Option A: Monorepo (Recommended)

```
analemma-web/
  frontend/          # Svelte or Vue SPA
    package.json
    src/
    vite.config.js
  backend/           # FastAPI API
    Dockerfile
    requirements.txt
    app.py
    analemma/        # Core engine (copied or symlinked)
  .github/
    workflows/
      deploy-frontend.yml
      deploy-backend.yml
  README.md
```

**Pros:**
- Single repo to manage, single set of issues/PRs
- Atomic commits that touch both frontend and backend
- Easier local development (one `git clone`)
- All major platforms support monorepos with per-directory build settings:
  - Vercel: set "Root Directory" to `frontend/`
  - Render: set "Root Directory" per service
  - DigitalOcean: set `source_dir` per component
  - Railway: set root path per service

**Cons:**
- CI/CD needs path filters so frontend deploys don't trigger on backend changes (and vice versa)
- Some platforms (Heroku) have weaker monorepo support

**GitHub Actions path filtering:**
```yaml
# .github/workflows/deploy-frontend.yml
on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
```

### Option B: Separate Repos

```
analemma-frontend/   # Svelte or Vue SPA
analemma-backend/    # FastAPI + engine code
```

**Pros:**
- Cleaner CI/CD -- each repo has exactly one deployment target
- Backend and frontend can have different contributor access
- Vercel/Netlify auto-detect everything without root directory config

**Cons:**
- Two repos to maintain
- Cross-repo changes require coordinated PRs
- Shared types or API contracts need a package or manual sync
- More friction for a solo developer

### Recommendation

**Use a monorepo.** For a single developer, the convenience of one repo far outweighs the minor CI/CD complexity. Every platform you'd use supports monorepos. Path-filtered GitHub Actions workflows keep deploys efficient.

## CI/CD Pipeline Options

### GitHub Actions (Recommended)

Free for public repos. 2,000 minutes/month for private repos on GitHub Free (students get GitHub Pro, which includes 3,000 minutes/month).

**For frontend (Vercel/Netlify):** You probably don't need a GitHub Actions workflow at all. Both Vercel and Netlify have their own Git integration -- they detect pushes and run builds automatically. GitHub Actions is only needed if you want to run tests before deploying.

**For backend deployment via GitHub Actions:**

#### Deploy to DigitalOcean App Platform
```yaml
name: Deploy Backend
on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}
      - name: Deploy to App Platform
        run: doctl apps create-deployment ${{ secrets.APP_ID }}
```

#### Deploy to Fly.io
```yaml
name: Deploy Backend
on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        working-directory: backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

#### Deploy to Render
Render auto-deploys from GitHub on push -- no GitHub Actions needed. But you can use Actions to run tests first:

```yaml
name: Test & Deploy Backend
on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/
  # Render auto-deploys on push; tests just act as a gate
```

#### Deploy to Heroku (Docker)
```yaml
name: Deploy to Heroku
on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: akhileshns/heroku-deploy@v3.13.15
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: analemma-api
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
          usedocker: true
          docker_build_args: ""
          appdir: backend
```

### Pre-deployment Testing

A basic CI pipeline worth setting up:

```yaml
name: CI
on:
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.changed_files, 'backend/')
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/

  test-frontend:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.changed_files, 'frontend/')
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - working-directory: frontend
        run: |
          npm ci
          npm run lint
          npm run build
```

## Custom Domain Setup

### Getting the Domain

You have two free domain options from the student pack:

1. **Namecheap:** Free `.me` domain for 1 year (e.g., `analemma.me`)
2. **Name.com:** Free domain from .live, .studio, .software, .app, .dev (e.g., `analemma.dev`, `analemma.app`)

**Recommendation:** Go with Name.com for a `.dev` or `.app` domain. These TLDs (owned by Google) enforce HTTPS by default (HSTS preloaded), which is a nice signal. `analemma.dev` is clean and professional. The `.me` TLD from Namecheap is fine too -- `analemma.me` works for a portfolio.

Claim both if you want -- they're free for a year.

### DNS Configuration

Most deployment platforms need you to add CNAME or A records. Here's how it works:

#### For split deployment (frontend on Vercel, backend on DO/Fly/Render):

| Record | Name | Value | Purpose |
|--------|------|-------|---------|
| CNAME | `@` or `analemma.dev` | `cname.vercel-dns.com` | Frontend (Vercel) |
| CNAME | `api` | `your-app.ondigitalocean.app` | Backend API |

Your frontend lives at `analemma.dev`, your API at `api.analemma.dev`. The frontend makes requests to `https://api.analemma.dev/process`.

Note: Some registrars (including Namecheap) don't support CNAME on the root domain. In that case:
- Use Vercel's A records for the root domain (Vercel provides specific IPs)
- Or use a `www` subdomain: `www.analemma.dev` -> Vercel, `api.analemma.dev` -> backend

#### For combo deployment (everything on DO App Platform):

| Record | Name | Value | Purpose |
|--------|------|-------|---------|
| CNAME | `@` or `analemma.dev` | `your-app.ondigitalocean.app` | Both frontend and API |

Path-based routing handles the rest: `/` serves the SPA, `/api/*` hits the backend.

#### For Heroku:

| Record | Name | Value | Purpose |
|--------|------|-------|---------|
| CNAME | `www` | `your-app.herokuapp.com` | Everything |
| ALIAS/ANAME | `@` | `your-app.herokuapp.com` | Root domain (if supported) |

Heroku doesn't support root CNAME. You need an ALIAS/ANAME record (Namecheap supports this via their "ALIAS" record type) or use a `www` subdomain.

### Connecting Namecheap

1. Log in to Namecheap Dashboard
2. Go to Domain List -> your domain -> "Advanced DNS"
3. Add a CNAME record: Host = `@` or `www`, Value = your platform's domain
4. Add a CNAME record: Host = `api`, Value = your backend's domain
5. Wait for DNS propagation (usually 5-30 minutes, up to 48 hours)

Render has an [official Namecheap guide](https://render.com/docs/configure-namecheap-dns).

### Connecting Name.com

1. Log in to Name.com
2. Go to your domain -> DNS Records
3. Add CNAME records as above
4. Name.com supports ALIAS records for root domains with some TLDs

### SSL/HTTPS

Every platform listed issues free SSL certificates automatically via Let's Encrypt. No manual setup needed. The `.dev` and `.app` TLDs enforce HTTPS via HSTS preloading -- browsers will refuse to connect over HTTP regardless of your server config.

The free SSL cert from Namecheap's student offer is unnecessary since every hosting platform provides automated certificates.

## Build Caching Strategy

Docker builds for our heavy backend will be slow without caching. Key optimizations:

1. **Layer ordering in Dockerfile:** Put `COPY requirements.txt` and `RUN pip install` before `COPY . .` so the dependency layer is cached unless requirements.txt changes.

2. **Platform build caching:** Render, Fly.io, and Railway all cache Docker layers between builds. DigitalOcean App Platform also caches.

3. **GitHub Actions Docker caching:** If building in CI:
```yaml
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

A cached rebuild (only code changes, not deps) should take under 60 seconds on most platforms.
