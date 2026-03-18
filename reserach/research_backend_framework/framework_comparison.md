# Framework Comparison: Detailed Analysis

## Quick Reference Table

| Criterion | FastAPI | Flask | Django | Starlette | Litestar |
|---|---|---|---|---|---|
| Setup complexity (for our case) | Low | Very Low | Medium-High | Low | Low |
| File upload handling | Built-in `UploadFile` | `request.files` | `request.FILES` + forms | `request.form()` | Built-in body parsing |
| Async native | Yes (ASGI) | No (WSGI, async bolt-on) | Partial (ASGI mode) | Yes (ASGI) | Yes (ASGI) |
| CPU-bound task handling | `run_in_executor` / process pool | Thread per request (Gunicorn) | Thread per request | `run_in_executor` / process pool | `sync_to_thread` built-in |
| Binary response | `Response(content, media_type)` | `send_file` / `Response` | `HttpResponse` | `Response(content, media_type)` | `Response(content, media_type)` |
| CORS | `CORSMiddleware` (one-liner) | flask-cors extension | `django-cors-headers` ext | `CORSMiddleware` | Built-in CORS config |
| OpenAPI docs | Auto-generated (Swagger + ReDoc) | Manual / flask-smorest | django-rest-framework | Manual / third-party | Auto-generated (Swagger + ReDoc + Stoplight + RapiDoc) |
| Type safety | Pydantic models | Manual | Serializers | Manual | Pydantic/dataclass/msgspec |
| Community size | Very large | Very large | Very large | Medium | Small but active |
| Learning curve | Low | Very low | High (if not already Django) | Low-Medium | Low-Medium |
| Deployment server | Uvicorn | Gunicorn | Gunicorn / Uvicorn | Uvicorn | Uvicorn |

---

## 1. FastAPI

**What it is:** ASGI framework built on top of Starlette and Pydantic. Designed for building APIs with automatic OpenAPI docs and type validation.

### Setup Complexity
Minimal for our use case. A single file can define the upload endpoint. Pydantic handles request validation. Install `fastapi[standard]` and you get Uvicorn included.

### File Upload Handling
First-class `UploadFile` class. Multipart parsing via `python-multipart` (included with standard install). The uploaded file is a SpooledTemporaryFile -- small files stay in memory, large files spill to disk automatically. Reads are async by default.

```
# Conceptual shape of our endpoint
@app.post("/process")
async def process_image(
    file: UploadFile,
    latitude: float = Form(...),
    longitude: float = Form(...),
    ...
) -> Response:
```

### Async and CPU-Bound Work
FastAPI runs on an async event loop (Uvicorn). The critical point: our computation is CPU-bound, not I/O-bound. Doing heavy numpy/scipy work directly in an `async def` handler would **block the event loop** and starve all other requests.

Two approaches:
- **Use `def` (not `async def`)** -- FastAPI automatically runs sync handlers in a threadpool. With GIL, this still serializes CPU work across threads, but at least the event loop stays responsive for accepting new connections.
- **Use `asyncio.get_event_loop().run_in_executor(ProcessPoolExecutor(), ...)` in an `async def` handler** -- offloads CPU work to a separate process, bypassing the GIL entirely. This is the correct solution for true CPU parallelism.

### Binary Image Response
Return `Response(content=image_bytes, media_type="image/png")`. FastAPI also has `StreamingResponse` for large files, but for a single processed image, a plain `Response` with bytes is fine.

### CORS
One-liner middleware:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

### Error Handling
Built-in exception handlers. Custom `HTTPException` with status codes. Pydantic validation errors automatically return 422 with details. For computation failures, you'd add a try/except in the handler and return a 500 with error info.

### Community and Docs
Massive community. 96k+ GitHub stars. Extensive documentation with tutorials covering every feature. Very active Discord. Tons of Stack Overflow answers and blog posts. The most popular Python API framework as of 2025-2026.

### Verdict for Our Use Case
Excellent fit. Minimal boilerplate, great file upload story, automatic API docs for testing, and clean async/process pool integration for CPU work.

---

## 2. Flask

**What it is:** WSGI "micro" framework. The original Python web micro-framework. Minimal core, extend with plugins.

### Setup Complexity
Extremely low. Five lines to get a working endpoint. The simplest framework to get started with if you've done any Python web work.

### File Upload Handling
Access via `request.files['fieldname']`. Returns a `FileStorage` object. You call `.read()` or `.save()` on it. Straightforward but slightly more manual than FastAPI's typed approach. No automatic large-file-to-disk spooling without configuring `MAX_CONTENT_LENGTH`.

### Async and CPU-Bound Work
Flask is WSGI -- fundamentally synchronous. Each request gets a thread (when run with Gunicorn's threaded workers or gevent). Flask 2.0+ added `async def` view support, but it's a bolt-on using `asyncio.run()` per request rather than a true event loop.

For CPU-bound work, Flask's synchronous model actually works in our favor in some ways: Gunicorn's `sync` worker type spawns separate processes via `--workers N`. Each process handles one request at a time, so CPU-bound work doesn't block other requests -- they go to other worker processes. This is a simple and effective concurrency model.

The downside: you need as many worker processes as concurrent users. Each process loads the full Python interpreter + all dependencies (numpy, astropy, scipy). Memory usage scales linearly.

### Binary Image Response
Flask's `send_file()` or `make_response()`:
```python
return Response(image_bytes, mimetype='image/png')
```
or 
```python
return send_file(io.BytesIO(image_bytes), mimetype='image/png')
```

### CORS
Requires `flask-cors` extension. Simple to use but it's an extra dependency.

### Error Handling
`@app.errorhandler(Exception)` decorators. Manual but flexible. No built-in validation like Pydantic -- you'd validate inputs manually or use something like marshmallow.

### Community and Docs
Huge community. 69k+ stars. Pallets project (well-maintained). Massive ecosystem of extensions. Every Python developer has used or seen Flask. Documentation is solid and battle-tested.

### Verdict for Our Use Case
Good fit. Simple, everybody knows it, and the synchronous process-based concurrency model via Gunicorn workers is actually well-suited for CPU-bound work. But no auto-generated API docs, no built-in input validation, and you'll need extensions for CORS. More boilerplate for the same result compared to FastAPI.

---

## 3. Django

**What it is:** "Batteries included" full-stack framework. ORM, admin panel, authentication, form handling, template engine, middleware, the works.

### Setup Complexity
Highest of all five options. Django requires a project structure (`manage.py`, settings module, URL config, views, etc.). The `startproject` + `startapp` scaffolding generates a lot of files you won't use. For a single-endpoint API, this is significant overhead.

If using Django REST Framework (DRF) for proper API support, that's another layer of complexity: serializers, viewsets, routers.

### File Upload Handling
Well-designed. `request.FILES` gives you `UploadedFile` objects. Django has configurable upload handlers -- files under 2.5MB stay in memory, larger ones go to temp files on disk. You can customize this threshold. The system is mature and handles edge cases well.

But it's designed around Django's form/model system. For a pure API without models, you're fighting the framework's opinions somewhat.

### Async and CPU-Bound Work
Django 4.1+ supports async views and ASGI deployment. But async support is still maturing -- the ORM is partially async, and many third-party packages are sync-only. Since we don't use the ORM or most of Django's features, this is less of an issue.

For CPU-bound work, same story as Flask: deploy with Gunicorn sync workers for process-based parallelism.

### Binary Image Response
```python
return HttpResponse(image_bytes, content_type='image/png')
```
Works fine, though it feels odd returning raw bytes from a framework designed for HTML pages and JSON APIs.

### CORS
Requires `django-cors-headers` third-party package. Well-maintained, widely used.

### Error Handling
Mature exception handling. Custom error views, middleware-based error handling, logging integration. Probably the most battle-tested error handling of any Python framework, but it's designed for HTML error pages -- JSON error responses require configuration.

### Community and Docs
Massive. 82k+ stars. The Django Software Foundation provides governance. Probably the best documentation of any Python framework. Huge ecosystem, tons of packages. But the ecosystem is oriented toward full-stack web apps, not lightweight APIs.

### Verdict for Our Use Case
Overkill. We use zero of Django's killer features (ORM, admin, auth, templates, forms). The setup overhead is significant. The framework's opinions about project structure, settings, and URL routing add complexity we don't need. DRF is excellent for CRUD APIs with databases, but that's not what we're building.

That said, if the project might grow to include user accounts, saved results, a gallery of processed images, etc. -- Django's batteries would pay off later.

---

## 4. Starlette

**What it is:** The ASGI toolkit that FastAPI is built on. Lightweight, low-level, high-performance. More a toolkit than a framework -- you get routing, middleware, and request/response handling, but no data validation layer.

### Setup Complexity
Low, but slightly more manual than FastAPI. You define routes explicitly (no decorator-based routing by default in the Starlette class, though `Route` objects work similarly). No Pydantic integration -- you parse and validate request data yourself.

### File Upload Handling
Via `request.form()` which returns form fields and uploaded files. Files are `UploadFile` instances (the same class FastAPI wraps). Requires `python-multipart`.

### Async and CPU-Bound Work
Identical to FastAPI since FastAPI is built on Starlette. Native ASGI, async event loop. Same `run_in_executor` pattern for CPU-bound work.

One difference: Starlette doesn't auto-threadpool sync handlers the way FastAPI does. If you define a sync handler, it blocks the event loop. You must use `async def` handlers and explicitly manage blocking work.

### Binary Image Response
```python
return Response(content=image_bytes, media_type="image/png")
```

### CORS
Built-in `CORSMiddleware`, same as FastAPI uses.

### Error Handling
Basic exception handling. No Pydantic validation layer. You write your own error responses.

### Community and Docs
Smaller community than FastAPI/Flask/Django. 12k stars. Documentation is minimal but sufficient -- it's a small surface area. Most community knowledge is actually in FastAPI's ecosystem, since FastAPI is built on Starlette.

### Verdict for Our Use Case
Fine, but there's no real reason to choose it over FastAPI. You get the same performance (they share the same ASGI core), but you lose auto-generated docs, Pydantic validation, and the larger ecosystem. The only advantage is a marginally smaller dependency footprint and slightly less "magic."

Pick Starlette if you want maximum control and minimal abstraction. Pick FastAPI if you want the same performance with better developer experience.

---

## 5. Litestar

**What it is:** Modern ASGI framework, forked from the Starlite project (itself inspired by FastAPI). More opinionated than FastAPI. Supports Pydantic, dataclasses, and msgspec for data validation. Built-in controller classes (NestJS-style).

### Setup Complexity
Low. Similar to FastAPI. Slightly different API style -- it uses `@get`, `@post` decorators imported from the package, and route handlers are registered on the `Litestar` app via a list, not decorators on the app instance.

### File Upload Handling
Supports `UploadFile` type annotation in handler parameters, similar to FastAPI. Also supports `Body` annotations with multipart configs. Requires `python-multipart`.

### Async and CPU-Bound Work
ASGI native. Has a useful built-in feature: `sync_to_thread=True/False` on route decorators. When `True`, sync handlers are automatically run in a thread pool. When `False`, they're expected to be non-blocking. This is more explicit than FastAPI's "def vs async def" distinction.

For CPU-bound work, same `run_in_executor` with `ProcessPoolExecutor` pattern as FastAPI/Starlette.

### Binary Image Response
Litestar has dedicated `File` and `Stream` response types. For returning processed image bytes:
```python
return Response(content=image_bytes, media_type="image/png")
```

### CORS
Built-in CORS configuration on the `Litestar` app -- no middleware import needed. Passed as a `cors_config` parameter.

### Error Handling
Built-in exception handling with configurable error responses. Supports validation errors from Pydantic, dataclasses, and msgspec. Similar to FastAPI's approach but with additional structure.

### Community and Docs
Smallest community of the five. ~6k stars. Active development with 5 core maintainers. Documentation is thorough but the ecosystem is young. Fewer third-party integrations, fewer Stack Overflow answers, fewer blog posts. If you hit an edge case, you may be reading source code.

### Verdict for Our Use Case
Capable and well-designed, but the small community is a real trade-off. The `sync_to_thread` feature is nice. The controller-based design is interesting but not needed for a single-endpoint API. Choose this if you want a modern, opinionated ASGI framework and don't mind being an early(ish) adopter.

---

## Head-to-Head: What Matters Most for Analemma

| Our Requirement | Best Option | Why |
|---|---|---|
| Minimal setup | Flask or FastAPI | Flask has less overhead; FastAPI has better DX for APIs |
| File upload | FastAPI or Litestar | Typed `UploadFile` with auto-validation |
| CPU-bound processing | Flask (Gunicorn sync) or FastAPI (ProcessPoolExecutor) | Flask's model is simpler; FastAPI's is more scalable |
| Return binary image | All are fine | Trivial in every framework |
| CORS | FastAPI, Starlette, Litestar | Built-in, no extra package needed |
| Auto API docs | FastAPI or Litestar | Swagger/ReDoc out of the box |
| Community / help | Flask, Django, or FastAPI | Largest ecosystems by far |
| Future extensibility | FastAPI or Django | FastAPI for API growth; Django if you need full-stack |
