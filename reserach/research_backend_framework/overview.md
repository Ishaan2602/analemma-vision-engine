# Backend Framework Research: Overview

Research conducted March 2026 for serving the Analemma Vision Engine as a web API.

## The Problem

We have a Python computation engine that:
- Accepts an image upload + metadata (GPS coords, datetime, camera specs)
- Detects the sun via CV (scipy connected-component labeling, numpy, Pillow)
- Calculates solar positions for a full year (astropy + JPL DE440 ephemeris)
- Overlays an analemma curve onto the original photo
- Returns a processed PNG/JPEG image
- Processing takes several seconds per request (CPU-bound)
- No database, no user accounts, no sessions

## API Surface

Minimal. One primary endpoint:

```
POST /process
  - Input: multipart form (image file + metadata fields)
  - Output: binary image (PNG/JPEG)
  - Processing time: 3-10 seconds depending on image size and precision mode
```

Possibly a health check and a metadata-only calculation endpoint, but the core is image-in, image-out.

## Frameworks Evaluated

| Framework | Version | Protocol | GitHub Stars (approx) | First Release |
|-----------|---------|----------|----------------------|---------------|
| FastAPI | 0.115+ | ASGI | ~96k | 2018 |
| Flask | 3.1+ | WSGI | ~69k | 2010 |
| Django | 5.1+ | WSGI/ASGI | ~82k | 2005 |
| Starlette | 1.0+ | ASGI | ~12k | 2018 |
| Litestar | 2.x | ASGI | ~6k | 2022 |

## Key Constraints

1. **CPU-bound workload** -- async frameworks don't automatically help here. The bottleneck is numpy/scipy/astropy math, not I/O wait.
2. **Large dependencies** -- astropy alone is ~100MB; scipy is ~70MB. Docker image size matters.
3. **File upload + binary response** -- framework must handle multipart upload and return raw image bytes cleanly.
4. **No ORM, no auth, no sessions** -- we don't need Django's batteries for this use case.
5. **Single developer** -- setup speed and maintenance simplicity matter.

## Research Files

- [framework_comparison.md](framework_comparison.md) -- Detailed per-framework analysis
- [concurrency_and_task_queues.md](concurrency_and_task_queues.md) -- CPU-bound handling, Celery vs sync, process pools
- [docker_and_deployment.md](docker_and_deployment.md) -- Containerization with heavy scientific packages, hosting options
- [recommendation.md](recommendation.md) -- Final recommendation with reasoning
