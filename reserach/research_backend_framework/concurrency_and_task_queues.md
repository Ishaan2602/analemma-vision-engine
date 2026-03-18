# Concurrency and Task Queues for CPU-Bound Work

This is the most important architectural decision for the Analemma API. The engine does heavy CPU work (numpy, scipy, astropy), and the choice of concurrency model determines how well the service handles multiple users.

## The Core Problem

Analemma processing is **CPU-bound**: 3-10 seconds of solid computation per request. This is fundamentally different from typical web API workloads (database queries, external API calls) which are I/O-bound.

- **I/O-bound** work benefits from async/await: the event loop handles thousands of connections while waiting on network/disk.
- **CPU-bound** work does not benefit from async. A numpy calculation running on the main thread blocks everything regardless of whether you use `async def` or `def`.

Python's GIL (Global Interpreter Lock) further complicates things: multiple threads in the same process can't do CPU work simultaneously. You need **multiple processes** for true CPU parallelism.

## Option 1: Synchronous Workers (Gunicorn prefork)

The simplest approach. Run Gunicorn with `sync` or `gthread` workers:

```
gunicorn app:app --workers 4 --timeout 30
```

Each worker is a separate OS process with its own Python interpreter and GIL. Requests are distributed across workers by the master process. One request per worker at a time (sync) or multiple threads per worker (gthread, but GIL limits CPU parallelism).

**How it works for us:**
- 4 workers = 4 concurrent image processes
- Each request gets a dedicated process -- no GIL contention
- Worker processes are forked, so they share memory for loaded libraries (copy-on-write)
- Simple, proven, zero additional infrastructure

**Pros:**
- Zero complexity. No task queues, no message brokers, no async patterns.
- Each request is fully isolated -- a crash in one computation doesn't affect others.
- Memory is mostly shared via fork() -- 4 workers don't use 4x memory for loaded libraries.
- Works with any framework (Flask, Django, FastAPI -- all support Gunicorn).

**Cons:**
- Concurrent users limited to worker count. If all 4 workers are processing, request #5 waits.
- The waiting request's HTTP connection is held open for potentially 10+ seconds. Clients might time out.
- Scaling means more workers = more memory. Each worker eventually diverges from shared memory.
- No request queuing beyond what Gunicorn's listen backlog provides.

**Best for:** Low to moderate traffic. If you expect fewer than ~10 concurrent users, this is the right answer.

### Memory Estimate

Each Python process with our full dependency stack loaded:
- Python interpreter: ~30MB
- numpy: ~30MB  
- scipy: ~40MB
- astropy (+ JPL DE440 ephemeris): ~150MB
- matplotlib: ~50MB
- Pillow: ~20MB
- Other deps: ~20MB
- **Per-worker baseline: ~340MB**
- Plus per-request image data: 5-50MB depending on image size
- **4 workers: ~1.4-1.6GB total** (less with copy-on-write sharing after fork)

In practice, forked workers share most of this via copy-on-write, so 4 workers might use ~600-800MB total rather than 1.4GB.

## Option 2: Async + ProcessPoolExecutor

Run an ASGI server (Uvicorn) and offload CPU work to a process pool:

```python
from concurrent.futures import ProcessPoolExecutor
import asyncio

pool = ProcessPoolExecutor(max_workers=4)

@app.post("/process")
async def process_image(file: UploadFile, ...):
    image_data = await file.read()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(pool, do_computation, image_data, metadata)
    return Response(content=result, media_type="image/png")
```

**How it works:**
- Uvicorn runs the event loop, handling HTTP connections efficiently
- CPU work is dispatched to a fixed pool of worker processes
- The event loop remains responsive while computation runs in background processes
- Results are returned to the event loop when ready

**Pros:**
- The HTTP server stays responsive even under load -- new connections are accepted immediately.
- Can handle many concurrent connections (some waiting for results, others being served).
- Clean separation: HTTP handling is async, computation is parallel.
- If you add I/O-bound features later (external API calls, cloud storage), the async layer handles them naturally.

**Cons:**
- More complex than sync workers. Serialization overhead for passing data to/from worker processes (images must be pickled).
- Worker processes still need the full dependency stack loaded.
- Debugging is harder -- errors in worker processes need to be propagated correctly.
- If the process pool is full, requests still queue up -- but at least the HTTP layer can return status/progress updates.

**Serialization concern:** Images are large (5-50MB). Passing them to worker processes via `ProcessPoolExecutor` requires pickling them through an inter-process pipe. For a 20MB image, this adds measurable overhead (hundreds of milliseconds). Alternatives:
- Write the image to a temp file, pass the path (cheaper to serialize, but adds disk I/O)
- Use shared memory (`multiprocessing.shared_memory`) -- faster but more complex

**Best for:** If you expect moderate to high traffic and want the HTTP layer to remain responsive.

## Option 3: Celery + Redis/RabbitMQ

Full task queue architecture:

```
Client -> API Server -> Redis/RabbitMQ -> Celery Worker(s) -> Result Store
```

The API server accepts the request, enqueues a task, and either:
- Returns a task ID immediately (async polling pattern)
- Holds the connection open until the result is ready (long-polling)

**Pros:**
- Decouples HTTP handling from computation entirely.
- Workers can run on separate machines -- horizontal scaling.
- Built-in retry logic, failure handling, monitoring (Flower dashboard).
- Task persistence -- if a worker crashes, the task can be retried.
- Natural fit for "submit job, check status, get result" UX patterns.
- Can prioritize tasks, rate-limit, set timeouts per-task.

**Cons:**
- Significant infrastructure complexity: Redis/RabbitMQ server, Celery workers, result backend.
- Three processes to manage: web server, message broker, Celery workers.
- Adds latency for the simple case: request -> enqueue -> dequeue -> process -> store result -> fetch result.
- Result storage: where does the processed image go? Redis (memory-intensive for large images), filesystem, S3?
- Overkill for low traffic. If you're processing < 100 images/day, this is a lot of machinery.
- Docker Compose goes from 1 container to 3+ containers.

**When to use it:**
- You expect sustained high concurrency (many simultaneous processing requests).
- You want a "submit and check back" UX rather than waiting for the response.
- You need horizontal scaling (add more Celery workers on separate machines).
- You need job retry logic (computation might fail for certain inputs).

## Option 4: Background Tasks (framework-level)

FastAPI and Litestar have built-in `BackgroundTask` support, but this is for fire-and-forget work (logging, sending emails). It runs **after** the response is sent and doesn't return results to the client. Not suitable for our use case where the client needs the processed image.

## Recommendation for Analemma

### Start with Option 1 (Sync Workers)

For initial deployment:

```
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 60 app:create_app()
```

Or if using FastAPI:
```
uvicorn app:app --workers 4 --timeout-keep-alive 60
```

This handles 4 concurrent requests with zero added complexity. If you're building an MVP, a portfolio project, or expect moderate traffic, this is the right call.

Set `--timeout 60` (or higher) because Gunicorn's default 30-second timeout will kill workers that are mid-computation.

### Upgrade to Option 2 if needed

If you find that:
- Users are getting connection timeouts waiting in the queue
- You want the API to stay responsive for health checks while processing
- You're adding I/O-bound features (saving results to cloud storage, etc.)

...then migrate the computation to a `ProcessPoolExecutor`. This is a code-level change, not an infrastructure change.

### Upgrade to Option 3 only if scaling demands it

If you need:
- More processing capacity than a single server provides
- Job queuing with status tracking
- Retry logic for failed computations
- Horizontal scaling across machines

...then add Celery. But don't start here. The infrastructure cost is real, and you can always add it later.

## Thread Pool vs Process Pool

| | Thread Pool | Process Pool |
|---|---|---|
| GIL limitation | Threads share the GIL -- can't do parallel CPU work | Each process has its own GIL -- true parallelism |
| Memory | Threads share memory (lightweight) | Processes have separate memory (heavier) |
| Data passing | Direct (shared memory) | Requires serialization (pickle) |
| Crash isolation | Thread crash can corrupt shared state | Process crash is fully isolated |
| Best for | I/O-bound work (network, disk) | CPU-bound work (our case) |

**For Analemma: use a process pool, not a thread pool, for computation.** Threads won't give you CPU parallelism due to the GIL. The only case for threads is if numpy releases the GIL during its C extensions (which it does for some operations), but scipy's connected-component labeling and astropy's coordinate transforms hold the GIL.

## Handling Long-Running Requests

With any approach, the client needs to handle multi-second response times:

1. **Simple wait:** Client sends request, waits for response. Set appropriate client-side timeout (30-60s). Works for most cases.

2. **Polling pattern:** API returns a job ID immediately. Client polls a `/status/{job_id}` endpoint. When done, client fetches result from `/result/{job_id}`. More complex but better UX for very slow requests.

3. **WebSocket:** Client connects via WebSocket, sends request, receives progress updates, then receives the result. Best UX but most complex to implement.

For an MVP, option 1 (simple wait) is fine. The processing takes 3-10 seconds, which is within typical HTTP timeout windows.
