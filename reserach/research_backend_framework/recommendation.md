# Recommendation

## TL;DR

**Use FastAPI** with Uvicorn workers for the initial deployment. Start with synchronous multiprocess workers (no task queue). Containerize with `python:3.12-slim`. Deploy to Render or Fly.io.

## Why FastAPI

The decision came down to FastAPI vs Flask. The other three options either add no value over FastAPI (Starlette) or add unneeded complexity (Django, Litestar).

### FastAPI over Flask

| Factor | FastAPI | Flask | Winner |
|---|---|---|---|
| File upload handling | Typed `UploadFile`, auto-spooling | `request.files`, manual | FastAPI |
| Input validation | Pydantic models, auto 422 errors | Manual or marshmallow | FastAPI |
| API documentation | Auto Swagger + ReDoc | Manual or extension | FastAPI |
| Binary responses | `Response(content, media_type)` | `Response` or `send_file` | Tie |
| CORS | Built-in middleware | flask-cors extension | FastAPI (marginal) |
| CPU-bound handling | `ProcessPoolExecutor` or sync workers | Gunicorn sync workers | Tie |
| Community | ~96k stars, very active | ~69k stars, very active | Tie |
| Learning curve | Slightly steeper (Pydantic, async) | Minimal | Flask |
| Deployment | Uvicorn, Docker | Gunicorn, Docker | Tie |

Flask would work fine. It's simpler and everybody knows it. But FastAPI gives us:
- Auto-generated Swagger UI for testing the upload endpoint during development without writing a frontend
- Typed parameters that catch malformed requests before they hit our engine code
- A modern async foundation that's easy to extend if we add I/O-bound features later

The learning overhead for someone who knows Flask is maybe an afternoon. The benefits accumulate over the life of the project.

### FastAPI over Django

Django is overkill. We don't need an ORM, admin panel, auth system, template engine, form library, or migration framework. We'd use 5% of Django's surface area and fight the rest of it. DRF is excellent for database-backed CRUD APIs, which this isn't.

If the project grew to include user accounts, saved results, and a gallery -- that would change the calculus. But for the current scope, Django's overhead isn't justified.

### FastAPI over Starlette

FastAPI is literally Starlette with Pydantic bolted on. Same ASGI core, same performance, but with validation, docs, and developer experience. There's no reason to go lower-level unless you have specific constraints around dependency size (FastAPI adds ~2MB over Starlette).

### FastAPI over Litestar

Litestar is well-designed and has some nice features (`sync_to_thread`, msgspec support, built-in CORS config). But the community is 15x smaller than FastAPI's. When you hit a problem at 2am, the number of Stack Overflow answers and GitHub issues matters. Litestar is worth watching but not the safe bet right now.

## Architecture for V1

```
                   +-------------------+
  HTTP Request --> |   Uvicorn (ASGI)  |
  (image upload)   |   4 workers       |
                   +-------------------+
                          |
                   +-------------------+
                   |   FastAPI app     |
                   |   - validate input|
                   |   - read upload   |
                   +-------------------+
                          |
                   +-------------------+
                   |  Analemma Engine  |
                   |  (same process)   |
                   |  - detect sun     |
                   |  - calc positions |
                   |  - render overlay |
                   +-------------------+
                          |
                   +-------------------+
                   |  Response         |
                   |  (image/png)      |
                   +-------------------+
```

V1: Uvicorn with `--workers 4`. Each worker handles one request at a time. The engine runs in the same process as the request handler. Simple, no inter-process serialization overhead, no task queue.

## When to Evolve

| Signal | Action |
|---|---|
| >5 concurrent users regularly queuing | Switch to `ProcessPoolExecutor` in async handlers |
| Need to track job status / show progress | Add Celery + Redis |
| Single server can't handle load | Add more Celery workers on separate machines |
| Need zero-downtime deploys | Move to container orchestration (ECS, Kubernetes) |
| Want instant response + polling | Add job queue pattern (POST returns job_id, GET polls status) |

Don't pre-optimize. Each step adds complexity that's only worth it at a specific scale threshold.

## Concrete Next Steps

1. Create a `web/` or `api/` directory in the project (or a single `app.py` at root)
2. Define one POST endpoint that accepts multipart form data (image + metadata fields)
3. Wire it to the existing `ImageAnchorer` pipeline
4. Return the processed image as a `Response` with `media_type="image/png"`
5. Add a health check endpoint (`GET /health`)
6. Write a Dockerfile based on `python:3.12-slim`
7. Pre-download the JPL DE440 ephemeris during the Docker build
8. Add a `.dockerignore` to keep the image lean
9. Deploy to Render or Fly.io from a GitHub push
10. Test with Swagger UI (auto-generated at `/docs`)

## Dependency Trimming for the API

The full `requirements.txt` includes packages the API endpoint doesn't need. Consider a separate `requirements-api.txt`:

**Keep:**
- numpy
- scipy
- astropy
- Pillow
- timezonefinder
- fastapi[standard]

**Evaluate removing:**
- matplotlib -- check if `ImageAnchorer` uses it for the overlay, or only for standalone plots
- pandas -- likely only used in analysis/notebooks
- plotly -- only used in notebooks/interactive charts

Removing matplotlib, pandas, and plotly could save ~115MB in the Docker image and reduce cold-start time.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Processing takes too long, HTTP timeout | Medium | High | Set generous server timeout (60s+), client-side timeout handling |
| Large image uploads exhaust memory | Low | High | Set `MAX_UPLOAD_SIZE`, validate image dimensions |
| Astropy ephemeris download fails in container | Low | Medium | Pre-download during Docker build |
| Concurrent requests overwhelm single server | Depends on traffic | Medium | Start with 4 workers, monitor, scale up |
| scipy/numpy version incompatibility in Docker | Low | Medium | Pin versions in requirements.txt, test in CI |
