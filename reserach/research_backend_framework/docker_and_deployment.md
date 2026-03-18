# Docker and Deployment Considerations

## The Heavy Dependencies Problem

Our dependency stack is large for a web API. The key offenders:

| Package | Installed Size (approx) | Notes |
|---------|------------------------|-------|
| astropy | ~100MB | Includes IERS data, unit definitions, coordinate frames |
| scipy | ~70MB | C/Fortran extensions, BLAS/LAPACK |
| numpy | ~30MB | Core numerical library |
| matplotlib | ~50MB | Plotting, font cache, backends |
| Pillow | ~20MB | Image codecs (libjpeg, libpng, etc.) |
| pandas | ~40MB | Not strictly needed for the API -- evaluate removing |
| plotly | ~25MB | Not strictly needed for the API -- evaluate removing |
| timezonefinder | ~40MB | Timezone shape data |
| JPL DE440 ephemeris | ~100MB | Downloaded by astropy on first use |

**Estimated total dependency size: ~475MB plus Python itself.**

A naive Docker image easily reaches 1.5-2GB. This matters for:
- Build time (CI/CD pipelines)
- Push/pull time to registries
- Cold start time on serverless/PaaS platforms
- Storage costs for image registries

## Docker Image Optimization

### Base Image Selection

| Base Image | Size | Build Complexity | Notes |
|---|---|---|---|
| `python:3.12` (Debian Bookworm) | ~1GB | Low | Everything "just works". Includes gcc, build tools. |
| `python:3.12-slim` | ~150MB | Medium | Smaller, but may need to install build deps for scipy/numpy wheels |
| `python:3.12-alpine` | ~50MB | High | musl libc causes issues with numpy/scipy. Avoid. |

**Recommendation: `python:3.12-slim`** with a multi-stage build. Modern numpy/scipy ship manylinux wheels with bundled BLAS, so they don't need system-level build tools at runtime. You only need build tools if you're compiling from source (unlikely with current wheels).

### Multi-Stage Build Strategy

```dockerfile
# Stage 1: Install dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime image
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY ./analemma ./analemma
COPY ./app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

This keeps the build tools out of the final image. The final image will still be ~800MB-1GB because the Python packages themselves are large, but you avoid carrying gcc, build-essential, etc.

### Reducing Image Size Further

1. **Remove unused dependencies:** The engine uses `pandas` and `plotly` for the interactive notebook and plotting, but the API endpoint only needs the core pipeline: `numpy`, `scipy`, `astropy`, `Pillow`, `timezonefinder`, `matplotlib`. If matplotlib is only used for standalone plotting (not the image overlay), it could be removed too -- the overlay rendering in `ImageAnchorer` uses Pillow's `ImageDraw`, not matplotlib.

   **Potential savings: ~65MB** by dropping pandas and plotly from the API's requirements.

2. **Pre-download ephemeris data:** Astropy downloads the JPL DE440 ephemeris (~100MB) on first use. Pre-download it during the Docker build to avoid a cold-start download and ensure reproducible builds:
   ```dockerfile
   RUN python -c "from astropy.coordinates import get_body; from astropy.time import Time; get_body('sun', Time.now())"
   ```

3. **Use `.dockerignore`:** Exclude `input_images/`, `output/`, `analysis.ipynb`, `docs/`, `.git/`, `__pycache__/`, `analemma_resources/` from the build context. These aren't needed in the container.

4. **Consider `uv` instead of pip:** The `uv` package manager from Astral is significantly faster for dependency resolution and installation. FastAPI's docs now recommend it for Docker builds. Build time drops from minutes to seconds for cached layers.

## Deployment Platform Comparison

### Render

| Aspect | Details |
|---|---|
| Docker support | Yes, native Dockerfile deployment |
| Free tier | Web service with 512MB RAM (not enough for our stack) |
| Paid tier | Starter at $7/month, 512MB RAM. Need at least $25/month plan for 2GB RAM. |
| Cold starts | Free tier spins down after inactivity. Paid tier stays running. |
| Disk | Ephemeral filesystem. Processed images need to be returned directly, not stored. |
| Build limits | 500 build minutes/month on free tier |

**Fit:** Good. Native Docker support, straightforward deploy-from-GitHub. Need at least 2GB RAM plan for our dependency stack. No cold-start issues on paid tier.

### Heroku

| Aspect | Details |
|---|---|
| Docker support | Yes, via `heroku.yml` or container registry |
| Dynos | Eco/Basic at $5-7/month, 512MB RAM. Standard-1X at $25/month, 512MB. Standard-2X at $50/month, 1GB. |
| Memory | 512MB - 2.5GB depending on dyno type. Performance-M at $250/month for 2.5GB. |
| Build | Heroku buildpack or Docker. Slug size limit of 500MB (tight for our deps). |
| Worker scaling | Easy dyno scaling |

**Fit:** Challenging. The 500MB slug size limit is a problem with our dependency stack. Docker deployment bypasses the slug limit but adds complexity. Memory constraints on cheaper dynos are tight. Expensive to get enough resources.

### AWS (ECS/Fargate, Lambda, EC2)

| Option | Cost | Scaling | Notes |
|---|---|---|---|
| EC2 (t3.small, 2GB RAM) | ~$15/month | Manual | Full control, cheapest for sustained workload |
| ECS/Fargate | ~$30-50/month | Auto-scaling | Docker native, no server management, pay per vCPU-second |
| Lambda | Per-invocation | Automatic | 10GB max memory, 15-min timeout, but cold starts are awful for our stack (30-60s to load astropy) |
| App Runner | ~$25/month | Auto-scaling | Simplest AWS container option, similar to Render |

**Fit:** EC2 or App Runner are the best AWS options. Lambda is a poor fit due to cold start times with heavy scientific packages. Fargate works but is priced above simpler alternatives for our workload.

### Fly.io

| Aspect | Details |
|---|---|
| Docker support | Native -- deploys from Dockerfile |
| Pricing | Shared CPU VMs from $3.19/month. 1GB RAM machines from ~$6/month. |
| Scaling | Auto-scaling, scale-to-zero available |
| Regions | Deploy close to users across many regions |

**Fit:** Good value. Docker-native, reasonable pricing, easy scaling. 2GB RAM machines are ~$12/month. The `fly deploy` workflow is simpler than most AWS setups.

### Railway

| Aspect | Details |
|---|---|
| Docker support | Native |
| Pricing | Usage-based. ~$5/month for light use, scales with CPU/RAM. |
| Memory | Configurable, up to 32GB |
| Build | Nixpacks or Dockerfile |

**Fit:** Good for MVPs. Usage-based pricing means you pay for what you use. Dockerfile support is solid.

### DigitalOcean App Platform

| Aspect | Details |
|---|---|
| Docker support | Yes |
| Pricing | Basic at $5/month (512MB -- too small). Professional at $12/month (1GB). |
| Scaling | Horizontal and vertical |

**Fit:** Decent. Need at least the Professional tier for enough memory.

## Platform Recommendation

For a project of this nature (portfolio/small-scale, CPU-heavy, needs 2GB+ RAM):

1. **Best value:** Fly.io or Railway -- Docker-native, reasonable pricing, simple deployment
2. **Best simplicity:** Render -- deploy from GitHub with a Dockerfile, managed infrastructure
3. **Best for production scale:** AWS App Runner or ECS/Fargate -- auto-scaling, but more AWS complexity
4. **Avoid:** Lambda (cold starts), Heroku (slug size limits, expensive for RAM), Alpine-based Docker images (numpy/scipy issues)

## Gunicorn / Uvicorn Configuration

### For Flask (WSGI)
```
gunicorn app:create_app() \
  --workers 4 \
  --timeout 60 \
  --bind 0.0.0.0:8000 \
  --max-requests 1000 \
  --max-requests-jitter 50
```

`--max-requests` restarts workers after N requests to prevent memory leaks from matplotlib/Pillow. The jitter prevents all workers restarting simultaneously.

### For FastAPI (ASGI)
```
uvicorn app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --timeout-keep-alive 60
```

Or via Gunicorn with Uvicorn workers:
```
gunicorn app:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --timeout 60 \
  --bind 0.0.0.0:8000
```

### Worker Count

Rule of thumb: `2 * CPU_cores + 1` for I/O-bound apps. For CPU-bound work like ours, `CPU_cores` workers is more appropriate -- each worker will peg one core. On a 2-core VM, use 2 workers. Adding more workers beyond core count just adds memory usage and context-switching overhead.

## .dockerignore

```
.git/
__pycache__/
*.pyc
input_images/
output/
analysis.ipynb
docs/
analemma_resources/
demo_scripts/
examples/
tests/
*.egg-info/
.github/
research_backend_framework/
```
