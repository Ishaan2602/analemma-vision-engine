# Project Architecture and Folder Structure

How to restructure the analemma_project repo for web deployment.

## Should We Split Frontend and Backend?

**Yes.** The reasons are practical, not just conventional:

1. **Different runtimes.** Frontend is static JavaScript/HTML/CSS. Backend is a Python process with heavy scientific libraries (~1 GB Docker image). They deploy to fundamentally different platforms.

2. **Different build tools.** Frontend uses Vite (or SvelteKit's build). Backend uses pip + Docker. Mixing these in a single build step is painful.

3. **Independent scaling.** The frontend is just static files on a CDN -- infinitely scalable at zero cost. The backend is a CPU-bound Python process that needs real compute. They have completely different resource profiles.

4. **Independent deployment.** You should be able to push a CSS fix to the frontend without redeploying the backend (and re-downloading the 500 MB JPL ephemeris).

5. **CORS is trivial.** The "downside" of splitting is CORS configuration. In FastAPI, that's four lines of middleware setup.

## Recommended Monorepo Structure

Keep everything in one GitHub repo, organized into clear directories:

```
analemma_project/
  frontend/                     # Svelte/SvelteKit app
    package.json
    svelte.config.js
    vite.config.js
    tailwind.config.js
    src/
      routes/                   # SvelteKit routes (single page for V1)
        +page.svelte            # Main app page
        +layout.svelte          # Shared layout
      lib/
        components/             # Svelte components
          ImageUpload.svelte
          MetadataForm.svelte
          LocationSearch.svelte
          AnalemmaViewer.svelte # SVG animation + image overlay
          SampleGallery.svelte
          DownloadButton.svelte
        utils/
          exif.js               # EXIF extraction (exifr wrapper)
          heic.js               # HEIC conversion (lazy-loaded heic2any)
          api.js                # Backend API client
          sensorLookup.js       # Camera sensor size lookup
      static/
        camera_sensors.json     # Lensfun-derived sensor DB
        samples/                # Thumbnails for sample gallery
    .env                        # VITE_API_URL=https://api.analemma.dev

  backend/                      # FastAPI API server
    Dockerfile
    requirements.txt            # API-only deps (no matplotlib/pandas/plotly)
    app.py                      # FastAPI application
    analemma/                   # Core engine (the existing package)
      __init__.py
      calculator.py
      sky_mapper.py
      plotter.py                # May be trimmed for API
      image_anchor.py
      metadata_parser.py
    api/
      routes.py                 # API endpoint definitions
      schemas.py                # Pydantic request/response models
      engine_wrapper.py         # Thin wrapper: API request -> engine pipeline

  engine/                       # Standalone engine (preserved for non-web use)
    (symlink or copy of analemma/ for CLI/notebook usage)

  input_images/                 # Sample images with metadata
    README.md                   # License table for all images
    brofjorden/
    hongkong/
    ...

  docs/                         # Project docs (kept at root)
  tests/                        # Engine tests
  examples/                     # Standalone engine examples

  .github/
    workflows/
      deploy-frontend.yml       # Vercel auto-deploys, but tests here
      deploy-backend.yml        # Build Docker, deploy to DO/Fly.io
      test.yml                  # Run engine tests on PR

  LICENSE                       # MIT license for code
  NOTICE                        # Third-party attribution (CC images)
  README.md                     # Updated project overview
  requirements.txt              # Full deps for local dev / notebooks
  analysis.ipynb
  analemma_cli.py
```

## Where Does the Engine Code Live?

This is the key structural decision. The analemma engine (`analemma/`) currently sits at the project root. For the web deployment, the backend needs the engine inside its Docker build context.

**Three options:**

### Option A: Copy engine into backend/ (Recommended for V1)

```
backend/
  analemma/         # Copy of the engine modules
  app.py
```

Simple. The backend is self-contained. The Dockerfile works without path tricks. The tradeoff: two copies of the engine code. But during active web development, the engine is stable and changes rarely.

For development, use a symlink or pip install in editable mode to avoid drift:
```bash
# In backend/
pip install -e ../    # If the root has setup.py/pyproject.toml
```

### Option B: Package the engine as a pip-installable library

Add a `pyproject.toml` at the root that makes `analemma` a proper Python package. The backend's `requirements.txt` installs it:

```
# backend/requirements.txt
analemma @ file:///app/engine   # Docker: copy engine dir, install from local path
```

This is cleaner long-term but requires setting up proper Python packaging (pyproject.toml, build system).

### Option C: Docker multi-stage build with shared context

```dockerfile
# Backend Dockerfile at repo root (not in backend/)
FROM python:3.12-slim
COPY analemma/ /app/analemma/
COPY backend/ /app/backend/
```

This uses the repo root as the Docker build context. Works, but the build context includes the entire repo (frontend, docs, images) unless you have a `.dockerignore`.

**Recommendation:** Start with Option A (copy). Move to Option B when the engine is mature and you're tired of syncing.

## Current Files That Stay at Root

These files serve the standalone engine and local development. They don't move:

- `requirements.txt` -- full dependency list for local dev / notebooks
- `analysis.ipynb` -- interactive testing (Jupyter)
- `analemma_cli.py` -- CLI entry point
- `create_input.py` -- input scaffolding tool
- `demo_scripts/` -- processing scripts
- `examples/` -- standalone usage examples
- `tests/` -- engine unit tests

The backend has its own `requirements.txt` with trimmed deps for deployment.

## GitHub Setup for Deployment

### Single Repo, Multiple Deploy Targets

```
GitHub repo: analemma_project
  |
  +--> Vercel (auto-deploy frontend/ on push to main)
  |      Root Directory: frontend/
  |      Framework: SvelteKit
  |      Build Command: npm run build
  |      Output Directory: build/
  |
  +--> DigitalOcean App Platform (deploy backend/ on push to main)
         Dockerfile: backend/Dockerfile
         Source Directory: backend/ (or repo root with .dockerignore)
```

Vercel connects to the repo directly -- push to `main` triggers a frontend build. DigitalOcean (or Fly.io/Render) deploys from the Dockerfile in `backend/`.

GitHub Actions path filtering ensures:
- Changes to `frontend/**` only trigger frontend tests + deploy
- Changes to `backend/**` or `analemma/**` only trigger backend tests + deploy
- Changes to `tests/**` trigger test runs but no deploys

### DNS Configuration

With a domain like `analemma.dev` from Name.com:
- `analemma.dev` -- CNAME to Vercel (frontend)
- `api.analemma.dev` -- CNAME to DigitalOcean / Fly.io (backend)

Both platforms auto-provision SSL via Let's Encrypt.
