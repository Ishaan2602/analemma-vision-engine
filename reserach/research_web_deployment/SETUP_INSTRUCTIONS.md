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

In your Name.com dashboard for your `.app` domain:

| Record Type | Host | Value | TTL |
|---|---|---|---|
| CNAME | `@` (or blank) | `cname.vercel-dns.com` | 300 |
| CNAME | `api` | `<your-do-app-url>.ondigitalocean.app` | 300 |

Then:

1. In Vercel project settings > Domains: add `analemmavision.app`
2. In DO App Platform settings > Domains: add `api.analemmavision.app`
3. Both platforms auto-provision SSL certificates

DNS propagation takes 5-60 minutes. After that:
- `https://analemmavision.app` serves the frontend
- `https://api.analemmavision.app` serves the backend

### 4.4 Update Environment Variables

Once DNS is live, update the Vercel environment variable:
- `VITE_API_URL` = `https://api.analemmavision.app`

Update the backend CORS config to allow the production frontend domain:
- `ALLOWED_ORIGINS` = `https://analemmavision.app`

Redeploy both after updating.

---

## Phase 5: Local Development Workflow

Once everything is scaffolded, this is how you work locally day-to-day.

### Run the frontend dev server

```bash
cd frontend
npm run dev
# Runs at http://localhost:5173
```

### Run the backend dev server

```bash
cd backend
pip install -r requirements.txt   # First time only
uvicorn app:app --reload --port 8000
# Runs at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### Test the backend Docker image locally

```bash
cd backend
docker build -t analemma-api .
docker run -p 8000:8000 analemma-api
# http://localhost:8000/docs for Swagger
```

### Run engine tests

```bash
pytest tests/
```

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
