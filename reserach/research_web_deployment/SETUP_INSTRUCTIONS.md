# Analemma Vision -- Setup Instructions

Follow these steps in order. Each section builds on the previous one. Don't skip ahead -- some steps depend on accounts and tools from earlier steps.

---

## Phase 1: Accounts and Credits

### 1.1 GitHub Student Developer Pack

If you haven't already, verify your student status at https://education.github.com/pack. You need this for:

- **Name.com**: free `.app` domain for 1 year
- **DigitalOcean**: $200 platform credit (expires 12 months after activation)
- **SimpleAnalytics**: free plan for student projects

### 1.2 Claim the Domain (Name.com)

1. Go to https://www.name.com/partner/github-students
2. Log in with your GitHub account
3. Search for your preferred `.app` domain (e.g., `analemmavision.app`)
4. If available, claim it (free for 1 year)
5. **Don't configure DNS yet** -- we'll do that after deployment is set up

Note: `.app` domains enforce HTTPS (it's built into the HSTS preload list). Both Vercel and DigitalOcean auto-provision SSL, so this is a non-issue.

### 1.3 Claim DigitalOcean Credits

1. Go to https://www.digitalocean.com/github-students
2. Sign up / link your GitHub student account
3. The $200 credit should appear on your account balance
4. You won't create anything on DO yet -- just make sure the credit is active

### 1.4 Vercel Account

1. Go to https://vercel.com/signup
2. Sign up with your GitHub account (this links the accounts for auto-deploy later)
3. The Hobby tier (free) is all you need
4. Don't create a project yet

### 1.5 LocationIQ API Key

1. Go to https://locationiq.com/
2. Create a free account
3. Go to your dashboard and copy the API access token
4. Save it somewhere -- you'll add it to your frontend `.env` later

### 1.6 SimpleAnalytics

1. Go to https://www.simpleanalytics.com/
2. Sign up (check if the student pack gives you direct access, otherwise the free trial works)
3. You'll get a script tag to add to your HTML -- save it for later

---

## Phase 2: Local Tooling

### 2.1 Node.js

SvelteKit requires Node.js 18+. Install Node.js 20 LTS (or later) if you don't have it:

- **Download**: https://nodejs.org/ (LTS version)
- **Verify**: `node --version` should show v20.x or higher
- **npm** comes bundled with Node.js

### 2.2 Docker Desktop

The backend deploys as a Docker container. Install Docker Desktop for local testing:

- **Download**: https://www.docker.com/products/docker-desktop/
- **Verify**: `docker --version` and `docker compose version`

### 2.3 Python 3.12

You likely already have Python from the engine development. Verify:

```bash
python --version   # Should be 3.12+
```

### 2.4 DigitalOcean CLI (doctl) -- optional but useful

```bash
# Windows (via scoop)
scoop install doctl

# Or download from https://docs.digitalocean.com/reference/doctl/how-to/install/
```

After installing:
```bash
doctl auth init   # Paste your DO API token when prompted
```

---

## Phase 3: Repository Restructuring

This is the big reorganization. The current project is a standalone Python engine. We're splitting it into a monorepo with `frontend/` and `backend/` alongside the existing engine code.

### 3.1 Current structure (what you have)

```
analemma_project/
  analemma/               <-- engine package
  analemma_cli.py
  analysis.ipynb
  create_input.py
  demo_scripts/
  docs/
  examples/
  input_images/
  output/
  reserach/               <-- research files (typo in folder name, that's fine)
  tests/
  requirements.txt
  README.md
  .gitignore
```

### 3.2 Target structure (what we're building toward)

```
analemma_project/
  frontend/                     <-- NEW: SvelteKit app
    package.json
    svelte.config.js
    vite.config.js
    tailwind.config.js
    src/
      routes/
        +page.svelte
        +layout.svelte
      lib/
        components/
        utils/
      static/
        camera_sensors.json
        samples/
    .env

  backend/                      <-- NEW: FastAPI API server
    Dockerfile
    .dockerignore
    requirements.txt
    app.py
    analemma/                   <-- copy of engine package
    api/
      routes.py
      schemas.py
      engine_wrapper.py

  analemma/                     <-- existing engine (stays for CLI/notebook use)
  analemma_cli.py               <-- stays
  analysis.ipynb                <-- stays
  create_input.py               <-- stays
  demo_scripts/                 <-- stays
  docs/                         <-- stays
  examples/                     <-- stays
  input_images/                 <-- stays (CC images for gallery, personal excluded)
  output/                       <-- stays
  reserach/                     <-- stays
  tests/                        <-- stays

  .github/
    workflows/
      deploy-frontend.yml       <-- NEW: frontend CI
      deploy-backend.yml        <-- NEW: backend CI/CD
      test.yml                  <-- NEW: PR test gate

  LICENSE                       <-- NEW: MIT license
  NOTICE                        <-- NEW: third-party attribution
  requirements.txt              <-- existing (full deps for local dev)
  README.md                     <-- updated
  .gitignore                    <-- updated
```

### 3.3 Create the frontend project

From the project root:

```bash
# Create the SvelteKit project
npx sv create frontend
```

When prompted:
- Template: **SvelteKit minimal**
- Type checking: **TypeScript**
- Additional options: select **prettier**, **eslint**, **tailwindcss**

Then:

```bash
cd frontend
npm install
```

Verify it works:

```bash
npm run dev
# Visit http://localhost:5173 -- you should see the SvelteKit welcome page
# Ctrl+C to stop
```

Install the adapter for static output (Vercel auto-detects SvelteKit, but we want the option):

```bash
npm install -D @sveltejs/adapter-static
```

Install frontend dependencies we'll need:

```bash
npm install exifr           # EXIF extraction (HEIC-capable, ~50KB)
npm install heic2any        # HEIC-to-JPEG conversion for browser preview
```

Create the frontend `.env` file:

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
VITE_LOCATIONIQ_TOKEN=your_locationiq_token_here
```

Return to project root:
```bash
cd ..
```

### 3.4 Create the backend project

```bash
mkdir backend
mkdir backend\api
```

Create `backend/requirements.txt` with trimmed dependencies (no matplotlib/pandas/plotly -- those are for notebooks, not the API):

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
numpy>=1.24.0
astropy>=5.3.0
scipy>=1.10.0
Pillow>=10.0.0
pillow-heif>=0.16.0
timezonefinder>=6.0.0
slowapi>=0.1.9
```

Copy the engine into the backend:

```bash
xcopy analemma backend\analemma /E /I
```

(On Linux/Mac: `cp -r analemma/ backend/analemma/`)

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system deps for Pillow and pillow-heif
RUN apt-get update && apt-get install -y --no-install-recommends \
    libheif-dev \
    libffi-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the JPL DE440 ephemeris (~17 MB) so it doesn't
# happen on the first request or on every cold start
RUN python -c "from astropy.coordinates import get_sun; from astropy.time import Time; get_sun(Time('2025-01-01'))"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

Create `backend/.dockerignore`:

```
__pycache__/
*.pyc
.env
.venv/
*.egg-info/
```

Create a minimal `backend/app.py` placeholder (the PLAN agent will flesh this out):

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Analemma Vision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Dev frontend
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
```

### 3.5 Create GitHub Actions workflows

Create `.github/workflows/` if it doesn't already exist:

```bash
mkdir .github\workflows
```

We'll create three workflow files. The PLAN agent will finalize these, but the scaffolding should exist.

**`.github/workflows/test.yml`** -- runs engine tests on every PR:

```yaml
name: Tests
on:
  pull_request:
    branches: [main]

jobs:
  test-engine:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

**`.github/workflows/deploy-backend.yml`** -- deploys backend to DO on push to main:

```yaml
name: Deploy Backend
on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'

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
        run: doctl apps create-deployment ${{ secrets.DO_APP_ID }}
```

The frontend auto-deploys via Vercel's GitHub integration -- no workflow needed for deployment. But you can add a test workflow:

**`.github/workflows/deploy-frontend.yml`** -- tests frontend on PR:

```yaml
name: Frontend CI
on:
  pull_request:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - working-directory: frontend
        run: npm ci
      - working-directory: frontend
        run: npm run build
```

### 3.6 Create LICENSE and NOTICE files

Create a `LICENSE` file at the project root with the MIT license text. Set the copyright holder to your name and year range (2025-2026).

Create a `NOTICE` file at the project root listing each CC-licensed sample image with its title, author, license, and source URL. Use the template from `reserach/research_licensing/repo_structure.md`.

### 3.7 Update .gitignore

Add nigeria to the personal photos exclusion block. Also add entries for the new frontend/backend directories:

The following lines need to be added to `.gitignore`:

```gitignore
# Nigeria personal photo
input_images/nigeria/
output/nigeria_output/

# Frontend
frontend/node_modules/
frontend/.svelte-kit/
frontend/build/

# Backend
backend/__pycache__/
backend/.env

# Environment files
.env
.env.local
```

---

## Phase 4: Deployment Setup

### 4.1 Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository (`analemma_project`)
3. Set **Root Directory** to `frontend`
4. Framework should auto-detect as **SvelteKit**
5. Add environment variables:
   - `VITE_API_URL` = `https://api.analemmavision.app` (your backend URL)
   - `VITE_LOCATIONIQ_TOKEN` = your LocationIQ token
6. Click Deploy

Vercel will now auto-deploy the frontend on every push to `main` that changes files in `frontend/`.

### 4.2 Deploy Backend to DigitalOcean App Platform

1. Go to https://cloud.digitalocean.com/apps/new
2. Choose GitHub as the source, select your repo
3. Set **Source Directory** to `backend`
4. App type: **Web Service**
5. Choose the **$25/mo** plan (1 vCPU, 2 GiB RAM) -- covered by student credit
6. Set the HTTP port to **8000**
7. Add environment variable:
   - `ALLOWED_ORIGINS` = `https://analemmavision.app` (your frontend domain)
8. Deploy

Note the app URL that DO gives you (something like `analemma-backend-xxxxx.ondigitalocean.app`). You'll use this temporarily until DNS is configured.

### 4.3 Configure DNS

**Vercel (frontend -- analemmavision.app):**

1. In the Vercel dashboard, go to your project > Settings > Domains
2. Add `analemmavision.app` as a custom domain
3. Vercel will show you the DNS records you need. For an apex domain (no `www`), it'll typically ask for either:
   - An **A record** pointing to Vercel's IP (76.76.21.21), or
   - A **CNAME** to `cname.vercel-dns.com` (only works if your DNS provider supports CNAME flattening at the apex)
4. Go to your **Name.com** dashboard > DNS Records for `analemmavision.app`
5. Add the record Vercel requested (A record is the safer choice for apex domains)
6. Back in Vercel, click "Verify" -- it will check DNS and auto-provision an SSL certificate

**DigitalOcean (backend -- api.analemmavision.app):**

1. In the DO App Platform dashboard, go to your app > Settings > Domains
2. Click "Add Domain"
3. Enter `api.analemmavision.app`
4. Choose **"You manage your domain"** (Option 2). DO doesn't need to be your nameserver -- your domain stays on Name.com.
5. DO will show you a CNAME target (something like `<your-app-slug>.ondigitalocean.app`)
6. Go to **Name.com** dashboard > DNS Records
7. Add a **CNAME record**:
   - Host: `api`
   - Value: the CNAME target DO showed you
   - TTL: 300 (or default)
8. Back in DO, click "Verify" or wait -- DO will detect the CNAME and provision SSL automatically

**Verification:**

DNS propagation usually takes 5-60 minutes. You can check progress:

```bash
# Check if the records are resolving (run in git bash or any terminal)
nslookup analemmavision.app
nslookup api.analemmavision.app
```

Once propagated:
- `https://analemmavision.app` should show your SvelteKit default page
- `https://api.analemmavision.app/health` should return `{"status":"ok"}`

If either shows a certificate error, wait a few more minutes -- SSL provisioning happens after DNS resolves.

### 4.4 Update Backend CORS for Production

The backend's `app.py` currently only allows `http://localhost:5173` (local dev). It needs to also allow the production frontend domain. Update `backend/app.py`:

Change the CORS `allow_origins` to read from an environment variable so it works in both local dev and production:

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Analemma Vision API")

# In development: defaults to localhost
# In production: set ALLOWED_ORIGINS=https://analemmavision.app on DO
allowed_origins = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

Then verify the DO environment variable:
1. Go to DO App Platform > your app > Settings > App-Level Environment Variables
2. Confirm that `ALLOWED_ORIGINS` is set to `https://analemmavision.app`
3. If you changed `app.py`, push to `main` -- DO will auto-redeploy from the `backend/` path

### 4.5 Verify the Vercel Environment Variables

1. Go to Vercel > your project > Settings > Environment Variables
2. Confirm these are set:
   - `VITE_API_URL` = `https://api.analemmavision.app`
   - `VITE_LOCATIONIQ_TOKEN` = your LocationIQ token (the `pk.xxx` value)
3. These should be set for the **Production** environment (and optionally Preview/Development)
4. Your local `frontend/.env` keeps `VITE_API_URL=http://localhost:8000` -- that's correct. Vite uses the local file during `npm run dev`, and Vercel's env vars during production builds. No conflict.

If you change any Vercel env var after the initial deploy, you need to **redeploy** for the change to take effect (Vercel > Deployments > click the three dots on the latest deployment > Redeploy).

### 4.6 End-to-End Smoke Test

Once DNS is propagated and both services are up:

1. **Frontend**: Visit `https://analemmavision.app` in your browser. You should see the SvelteKit default page. Open the browser console (F12 > Console) and check for errors -- there shouldn't be any.

2. **Backend health check**: Visit `https://api.analemmavision.app/health` in your browser. You should see:
   ```json
   {"status": "ok"}
   ```

3. **CORS check**: Open the browser console on your frontend page and run:
   ```javascript
   fetch('https://api.analemmavision.app/health')
     .then(r => r.json())
     .then(d => console.log(d))
     .catch(e => console.error(e))
   ```
   If CORS is configured correctly, you'll see `{status: "ok"}` logged. If you see a CORS error, double-check the `ALLOWED_ORIGINS` env var on DO matches your frontend domain exactly (including `https://`, no trailing slash).

4. **Swagger UI**: Visit `https://api.analemmavision.app/docs` -- you should see FastAPI's auto-generated Swagger documentation page with the `/health` endpoint listed.

### 4.7 Set Up GitHub Actions Secrets

The deploy-backend workflow needs two secrets to trigger DO deployments from GitHub Actions:

1. Go to your GitHub repo > Settings > Secrets and variables > Actions
2. Add these repository secrets:
   - **`DIGITALOCEAN_ACCESS_TOKEN`**: Your DigitalOcean API token (the same one you used with `doctl auth init`). If you don't have it saved, generate a new one at DO > API > Tokens.
   - **`DO_APP_ID`**: Your app's ID on DO App Platform. Find it by running in your PowerShell (where doctl is configured):
     ```powershell
     doctl apps list --format ID,Spec.Name
     ```
     Copy the ID (a UUID like `a1b2c3d4-...`).

3. To verify, push any small change to a file in `backend/` (like adding a comment to `app.py`). Watch the Actions tab on GitHub -- the "Deploy Backend" workflow should trigger and succeed.

---

## Phase 5: Local Development Workflow

Once everything is scaffolded, this is how you work locally day-to-day.

### 5.1 Run the frontend dev server

```bash
cd frontend
npm run dev
# Runs at http://localhost:5173
# Hot-reloads on file changes
# Uses VITE_API_URL=http://localhost:8000 from frontend/.env
```

### 5.2 Run the backend dev server

You need a separate terminal for this (open a new git bash tab or use the VS Code terminal split).

```bash
cd backend
pip install -r requirements.txt   # First time only
uvicorn app:app --reload --port 8000
# Runs at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
# --reload watches for file changes and restarts automatically
```

With both running, the frontend at :5173 talks to the backend at :8000 locally. The CORS config allows `http://localhost:5173` by default.

### 5.3 Test the backend Docker image locally

Before pushing a Dockerfile change, verify it builds and runs:

```bash
cd backend
docker build -t analemma-api .
docker run -p 8000:8000 analemma-api
# Visit http://localhost:8000/docs for Swagger
# Ctrl+C to stop the container
```

The first build will be slow (~5-10 minutes) because it downloads the ephemeris and installs scientific packages. Subsequent builds are fast thanks to Docker layer caching.

### 5.4 Run engine tests

From the project root:

```bash
pytest tests/
```

### 5.5 Git workflow

The typical flow for making changes:

```bash
# 1. Make changes to frontend/ and/or backend/
# 2. Test locally (npm run dev / uvicorn)
# 3. Commit and push
git add .
git commit -m "description of changes"
git push origin main
```

On push to `main`:
- Changes in `frontend/` trigger a Vercel auto-deploy (instant, no GitHub Action needed)
- Changes in `backend/` trigger the GitHub Action which calls `doctl apps create-deployment`
- Changes in `tests/` or root Python files don't trigger any deploy

---

## Phase 6: External Service Integration Checklist

These get wired in during implementation (the PLAN agent will detail the order):

- [ ] LocationIQ autocomplete integrated into the frontend location input
- [ ] exifr integrated for client-side EXIF extraction
- [ ] heic2any integrated for browser HEIC preview
- [ ] camera_sensors.json built from lensfun data and served from frontend/static/
- [ ] SimpleAnalytics script tag added to the HTML head
- [ ] slowapi rate limiter added to FastAPI (10-20 req/min per IP)
- [ ] User-facing error message translation layer in the API

---

## Prep Summary

Before handing off to the PLAN agent, you should have:

1. **Accounts ready**: GitHub (with student pack), Name.com domain claimed, DigitalOcean credit active, Vercel account, LocationIQ API key
2. **Local tools installed**: Node.js 20+, Docker Desktop, Python 3.12+
3. **Repo restructured**: `frontend/` scaffolded with SvelteKit + Tailwind, `backend/` scaffolded with Dockerfile + placeholder app.py, engine code copied into backend, `.github/workflows/` created
4. **LICENSE and NOTICE files** at repo root
5. **`.gitignore` updated** with nigeria + frontend/backend entries

Once these are in place, prompt the PLAN agent with a reference to the finalized decisions file (`reserach/research_web_deployment/FINALIZED_DECISIONS.md`) and the full research directory. The PLAN agent will generate the detailed implementation plan covering every component, endpoint, component, and integration step.
