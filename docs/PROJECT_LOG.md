# Analemma Project -- Session Log

Most recent work at the top.

---

## Session 4 -- started 2026-03-18

### Prompt 6 (2026-03-18) -- Refinements: charts 500 fix, text naturalization

Three fixes:
1. Charts 500 error: the deployed server hadn't rebuilt with matplotlib yet. The code itself works locally. Added ValueError/RuntimeError handling to the /api/charts route (was only catching generic Exception). The root cause is that the DigitalOcean container needs to rebuild with the updated requirements.txt that now includes matplotlib.
2. Naturalized About and Methodology page text. Reduced `--` (double-hyphen) usage, broke up formulaic sentence/paragraph structures, removed cookie-cutter summary patterns, varied paragraph length and connective tissue. Converted bullet-list sections to flowing prose where appropriate (especially the Limitations section). Let some paragraphs end without neat closings.
3. No media elements were created for the info pages. Explained to user that the pages are text-only (no images or diagrams are served from the app), and any media would need to be added as static assets in `frontend/static/` and referenced via `<img>` tags in the pages.

### Prompt 5 (2026-03-18) -- Feature batch: chart viewer, sun picker, info pages

Implemented three major features that were planned at the end of Prompt 4.

**Feature 1 -- Sky Chart & Figure-8 Viewer:**
- Backend: new `POST /api/charts` endpoint in routes.py that takes lat/lon/datetime and returns base64-encoded PNG sky chart and figure-8 via matplotlib (Agg backend). Added matplotlib to requirements.txt.
- Frontend: ChartViewer.svelte component with collapsible dropdown, lazy-loaded chart images, and per-chart save buttons. Mounted below AnalemmaViewer in +page.svelte.

**Feature 2 -- Click-to-Select Sun Position:**
- SunPicker.svelte: full-viewport modal overlay, click-to-mark with crosshair, confirm/cancel buttons, Escape to close. Computes actual pixel coords from displayed-to-natural coordinate ratio.
- MetadataForm.svelte: replaced raw X/Y numeric inputs with a picker-based UI. Shows "Select sun position on image" button, or read-only coords with Clear/Reselect when set. Amber warning banner when auto-detection fails.
- +page.svelte: added detectionFailed state, error message parsing in generate() to detect sun detection failures, SunPicker mount and confirm/cancel handlers, new props passed to MetadataForm.

**Feature 3 -- Educational Info Pages:**
- +layout.svelte: added tabbed navigation (App, About, Methodology) with amber active highlight, responsive desktop/mobile layout.
- about/+page.svelte: explains what an analemma is, why it forms (axial tilt + eccentricity), how it varies by location, and what the app does.
- methodology/+page.svelte: covers solar position computation (Astropy/DE440), horizon coordinate transform, camera model (tangent-plane projection with cos(alt) correction), CV sun detection pipeline, overlay rendering, and limitations.

**Verification:** svelte-check 0 errors, npm run build clean, Python AST parse OK.

### Prompt 4 (2026-03-18) -- Fix sample rendering, SVG styling, mobile save

User tested the live app and reported 6 issues. Investigation, planning, and implementation all done in one pass.

**Root causes found:**
1. Wrong analemma for hongkong -- thumbnail was generated without EXIF transpose, producing a 400x300 landscape image from a 2592x3456 portrait original. Sun auto-detection on the wrong-orientation compressed JPEG picked entirely different pixels.
2. Wrong analemma for other samples -- 400px compressed thumbnails caused brightest-pixel detection to drift vs. full-res originals. All 6 samples affected to varying degrees.
3. Connecting line across image -- single continuous SVG path connected all in-bounds points chronologically. When the analemma exits bounds and re-enters elsewhere, the path drew a diagonal line across the image.
4. Low-quality sample images -- 400px wide, JPEG quality 85.
5. Lines/dots too thick in SVG overlay.
6. raghav2 wrong analemma -- turned out to be wrong test metadata (user entered 35mm-equivalent focal length). No code changes needed; output is correct with proper metadata.

**Fixes applied:**
- `scripts/generate_thumbnails.py` -- EXIF transpose before resize, 1200px wide (was 400px), quality 90.
- Regenerated all 6 thumbnails. Hongkong now correctly 1200x1600 portrait.
- Pre-computed sun pixel positions from full-res originals, scaled to 1200px coords, stored in sample metadata on both frontend (`samples.ts`) and backend (`routes.py`, `schemas.py`).
- `AnalemmaViewer.svelte` -- SVG path now uses gap detection (median spacing * 4 threshold) to break into separate segments at discontinuities.
- Reduced dot radius (2-5px, was 3-8), stroke width (1-2px, was 2+), anchor/label sizing.
- Added client-side Save button: renders image+SVG to canvas, exports PNG. Touch devices also open in new tab for long-press save.

### Prompt 3 (2026-03-18) -- Fix matplotlib import error

Backend was still 500ing after the ThreadPoolExecutor fix. The new logging revealed `ModuleNotFoundError: No module named 'matplotlib'`. The import chain was: `image_anchor.py` -> `analemma/__init__.py` -> `plotter.py` -> `import matplotlib`. Two fixes: removed `AnalemmaPlotter` from the backend `__init__.py` (API never uses it), and made the `import matplotlib` in `image_anchor.py` lazy (inside `create_composite_plot()`, which the API also never calls). Verified locally that the import chain works clean.

### Prompt 2 (2026-03-18) -- Production bugfix and cleanup

Debugged 500 Internal Server Error on `/api/analyze` in production (DigitalOcean App Platform).

**Root cause:** `ProcessPoolExecutor` spawning child processes inside uvicorn's multi-worker environment caused failures in DO's containerized runtime. All requests hit the generic `except Exception:` handler, but no logging was configured so the actual traceback was invisible in the runtime logs.

**Fixes applied:**
- `backend/api/engine_wrapper.py` -- replaced `ProcessPoolExecutor` with `ThreadPoolExecutor`. uvicorn `--workers 2` already gives process-level parallelism; the thread pool just keeps the async event loop unblocked.
- `backend/api/routes.py` -- added `logger.exception()` calls in both `/api/analyze` and `/api/render` error handlers so future exceptions are visible in DO logs. Added `/api/health` endpoint to the router.
- `backend/app.py` -- added `logging.basicConfig(level=logging.INFO)` so log output actually reaches stdout.
- `frontend/src/routes/+layout.svelte` -- fixed GitHub link to `https://github.com/Ishaan2602/analemma-vision-engine`.

Committed and pushed. The push will trigger auto-deploy on both Vercel (frontend) and DO App Platform (backend).

### Prompt 1 (2026-03-18) -- Full web app implementation

Implemented the entire Analemma Vision web app across 6 phases, following the plan generated by the PLAN agent in Session 3.

**Phase 1 (Backend API):** Already completed in the prior prompt.
- `backend/api/schemas.py` -- 7 Pydantic response models
- `backend/api/engine_wrapper.py` -- ProcessPoolExecutor with async wrappers
- `backend/api/routes.py` -- POST /api/analyze, POST /api/render, GET /api/samples
- `backend/app.py` -- slowapi rate limiting, router mount, pillow-heif startup

**Phase 2 (Frontend Utilities):** Already completed in the prior prompt.
- `frontend/src/lib/utils/api.ts` -- backend API client with TypeScript interfaces
- `frontend/src/lib/utils/exif.ts` -- EXIF extraction via exifr
- `frontend/src/lib/utils/sensorLookup.ts` -- 3-tier sensor size detection
- `frontend/src/lib/utils/heic.ts` -- HEIC detection + conversion
- `frontend/src/lib/utils/geocoding.ts` -- LocationIQ autocomplete

**Phase 3 (Svelte Components):**
- `ImageUpload.svelte` -- drag-drop upload zone, EXIF extraction, HEIC preview conversion
- `LocationSearch.svelte` -- debounced autocomplete with keyboard navigation
- `MetadataForm.svelte` -- all metadata fields with 3-tier sensor auto-fill + source badges
- `AnalemmaViewer.svelte` -- SVG overlay with path draw animation, staggered dots, date labels, hover tooltips, replay button
- `SampleGallery.svelte` -- horizontal scroll gallery of 6 CC images
- `DownloadButton.svelte` -- fetches /api/render and triggers PNG download

**Phase 4 (Main Page Assembly):**
- `+page.svelte` -- split-panel layout (60/40), composes all components, state management, generate/download flow
- `+layout.svelte` -- dark theme with amber accent, header with GitHub link, footer
- `layout.css` -- CSS custom properties for dark palette, Inter font, scrollbar styling
- `app.html` -- meta tags (OG, Twitter), Inter font via Google Fonts, SimpleAnalytics

**Phase 5 (Static Assets):**
- `scripts/generate_thumbnails.py` -- resizes input images to 400px-wide JPEG thumbnails
- Generated 6 thumbnails in `frontend/static/samples/`
- `frontend/src/lib/data/samples.ts` -- hardcoded sample image metadata
- `frontend/static/camera_sensors.json` -- 120+ cameras from major brands (Canon, Nikon, Sony, Fujifilm, Apple, Samsung, etc.)

**Phase 6 (Polish):**
- CORS defaults verified (localhost dev, ALLOWED_ORIGINS env for production)
- Meta tags + OG tags in app.html
- SimpleAnalytics script in app.html
- Inter font loaded via Google Fonts

**Verification:**
- `npm run build` passes (170 modules, 0 errors)
- `npm run check` passes (0 errors, 3 warnings fixed)
- All backend Python files pass AST syntax check
- Backend deps not installed locally (Docker-only) -- syntax verified

---

## Session 3 -- started 2026-03-17

### Prompt 9 (2026-03-17) -- Phase 3 setup execution

Executed the remaining steps of Phase 3 from SETUP_INSTRUCTIONS.md. User had already completed steps 3.1-3.3 (SvelteKit project created with `npx sv create frontend`), but missed ESLint and Tailwind CSS during the interactive setup.

**Fixes applied:**
- Added Tailwind CSS via `npx sv add tailwindcss` (Vite plugin + layout.css configured automatically)
- Manually installed ESLint with svelte + typescript plugins, created `eslint.config.js`, added `lint` and `format` scripts to package.json

**Step 3.4 -- Backend created:**
- `backend/` directory with `app.py` (FastAPI placeholder with CORS), `requirements.txt` (trimmed deps -- no matplotlib/pandas/plotly), `Dockerfile` (python:3.12-slim, ephemeris pre-download), `.dockerignore`
- Engine copied into `backend/analemma/`
- API scaffold: `api/routes.py`, `api/schemas.py`, `api/engine_wrapper.py` (placeholders for PLAN agent)

**Step 3.5 -- GitHub Actions workflows:**
- `.github/workflows/test.yml` -- engine tests on PR
- `.github/workflows/deploy-backend.yml` -- DO App Platform deploy on push to backend/
- `.github/workflows/deploy-frontend.yml` -- frontend build check on PR

**Step 3.6 -- LICENSE and NOTICE:**
- `LICENSE` -- MIT, copyright Ishaan2602
- `NOTICE` -- full attribution for all 6 CC-licensed sample images + planned lensfun reference

**Step 3.7 -- .gitignore updated:**
- Added frontend entries (node_modules, .svelte-kit, build)
- Added backend entries (__pycache__, .env)

**Notes:**
- The VS Code `.env` warning about Python terminal injection is irrelevant -- Vite reads `.env` files on its own via the `VITE_` prefix convention
- doctl installed and authenticated via PowerShell (separate from git bash terminal)
- LocationIQ token already set in `frontend/.env`

**Next step:** User prompts the PLAN agent with FINALIZED_DECISIONS.md and the research directory to generate the implementation plan.

### Prompt 8 (2026-03-17) -- Decisions finalized + setup instructions generated

User reviewed all 15 decision questions from `DECISIONS_REQUIRED.md` and the additional considerations. All decisions locked in. Chose the recommended path for each question, with these specific overrides:

- Q4: `.app` TLD (not `.dev`)
- Q10: Day 1 Extended (JPEG + HEIC + PNG + WebP)
- Q11: nigeria added to .gitignore alongside raghav/robert exclusions
- Q15: Project name is "Analemma Vision"

Additional considerations accepted: two-phase response (JSON fast, PNG on download), 30 MB upload limit, Dockerfile ephemeris pre-download, basic rate limiting (slowapi), helpful error messages, SimpleAnalytics, localStorage caching for geocoding and sensor lookups. Accessibility compliance not a V1 priority.

**Files created:**
- `reserach/research_web_deployment/FINALIZED_DECISIONS.md` -- all 15 answers + additional considerations in one reference file
- `reserach/research_web_deployment/SETUP_INSTRUCTIONS.md` -- 6-phase step-by-step guide covering accounts, local tooling, repo restructuring, deployment setup, local dev workflow, and integration checklist

**Changes made:**
- `.gitignore` updated: added `input_images/nigeria/` and `output/nigeria_output/`

**Next step:** User follows the setup instructions, then prompts the PLAN agent with the finalized decisions and full research directory to generate the implementation plan.

### Prompt 7 (2026-03-17) -- Comprehensive web deployment research

Full research sprint covering every aspect of deploying the analemma engine as a web application. This was a research-only prompt -- no code changes.

**What was researched:**
- Frontend frameworks (Svelte vs Vue vs React vs Astro vs Next.js vs vanilla)
- Backend API frameworks (FastAPI vs Flask vs Django vs Starlette vs Litestar)
- Deployment platforms with student pack credits (Vercel, DigitalOcean, Heroku, Fly.io, Render, AWS)
- Geocoding APIs for location autocomplete (10 services compared)
- Camera sensor size auto-detection (EXIF crop factor, lensfun DB, manual fallback)
- EXIF extraction from HEIC and other formats
- Image format compatibility (browser + server)
- Analemma SVG animation approaches
- Licensing analysis (MIT code + CC images, ShareAlike implications)
- Project architecture and monorepo folder structure
- Frontend design concepts and responsive layout
- CI/CD pipelines and GitHub Actions workflows
- Custom domain setup

**Research directories created:**
- `research_frontend_frameworks/` (4 files)
- `research_backend_framework/` (5 files)
- `research_deployment/` (6 files)
- `research_web_app_apis/` (4 files)
- `research_image_handling/` (4 files)
- `research_licensing/` (6 files)
- `research_web_deployment/` (4 files -- architecture, design, decisions, considerations)

**Key recommendations from research:**
- Svelte/SvelteKit for frontend (built-in `draw` transition for analemma animation)
- FastAPI for backend (auto-generated docs, typed validation)
- Vercel (frontend) + DigitalOcean (backend) for initial deployment, using student credits
- LocationIQ for geocoding (5K req/day free, autocomplete, no map requirement)
- Three-tier sensor detection: EXIF crop factor -> lensfun JSON -> manual
- SVG path animation overlaid on the image, with JSON data from the backend
- MIT license for code, CC licenses preserved per-image

**Next step:** User answers the 15 decision questions in `research_web_deployment/DECISIONS_REQUIRED.md`. Those answers feed into setup instruction files, which the PLAN agent will use to build the full implementation plan.

### Prompt 6 (2026-03-17) -- Image handling research (EXIF, formats, animation)

Deep-dive research into three interconnected topics for the web application layer:

1. **EXIF extraction from uploaded images (including HEIC)** -- compared JS libraries (exifr, exif-js, piexifjs) and Python libraries (Pillow, pyexiftool, ExifRead) for extracting GPS, focal length, sensor dimensions, and datetime from user uploads. exifr is the clear winner on the client side (fast, HEIC-native, tree-shakeable). On the server, Pillow's built-in `getexif()` + `pillow-heif` for HEIC is sufficient. Architecture: extract EXIF client-side with exifr for instant form pre-fill, send original file to server, server re-extracts as ground truth.

2. **Image format compatibility** -- built a format matrix covering browser display, Pillow processing, and EXIF availability for JPEG, PNG, HEIC/HEIF, WebP, TIFF, BMP, and RAW. V1 must-support: JPEG plus HEIC (covers 90%+ of phone uploads). Should-support: PNG, WebP, HEIF. Skip: TIFF, BMP, RAW. heic2any handles client-side HEIC-to-JPEG conversion for preview; server uses pillow-heif to process originals natively.

3. **Analemma animation** -- compared SVG path animation, HTML5 Canvas, CSS keyframes, and JS animation libraries (GSAP, Motion One, Framer Motion, Lottie). SVG path with Svelte's built-in `draw` transition is the top pick -- zero dependencies, declarative, and perfectly suited for the figure-8 curve. Backend needs a new `get_analemma_json()` method on ImageAnchorer to return point data as JSON instead of only rendering to a static image.

New dependencies identified: exifr (client), heic2any (client), pillow-heif (server).

Files created:
- `research_image_handling/overview.md`
- `research_image_handling/exif_extraction.md`
- `research_image_handling/image_format_compatibility.md`
- `research_image_handling/analemma_animation.md`

### Prompt 5 (2026-03-17) -- Geocoding API + Camera Sensor Size research

Researched two API integration points for the web app:

**Geocoding / Place Autocomplete**: Compared 10 services (Google Places, Mapbox, Nominatim, Photon, Geoapify, LocationIQ, MapTiler, Pelias, Algolia Places, PlaceKit) across free tier, autocomplete support, accuracy, frontend widgets, ToS/attribution, latency, and worldwide coverage.

Key findings:
- Google and Mapbox both require results displayed on their proprietary maps (ToS problem for us)
- Algolia Places is dead (sunset May 2022)
- Nominatim has no autocomplete; Photon/Pelias are too heavy to self-host for a hobby project
- LocationIQ wins for V1: 5K req/day free, autocomplete endpoint, no map requirement, worldwide OSM data
- Geoapify and MapTiler are solid alternatives

**Camera Sensor Size**: Evaluated 7 approaches -- static JSON, lensfun database, ExifTool, browser EXIF (exifr), online databases (digicamdb), crop factor math from EXIF, crowdsourced DB.

Key findings:
- exifr (npm, 794K weekly downloads, MIT) can extract Make, Model, FocalLength, FocalLengthIn35mmFormat client-side in ~1ms
- Crop factor = FocalLengthIn35mmFormat / FocalLength, then sensor_width = 36/cropfactor (for 3:2 sensors)
- Lensfun's XML database (CC BY-SA 3.0) stores cropfactor per camera -- can be parsed at build time into a JSON lookup
- Recommended hybrid: browser EXIF + crop factor math (80% coverage) -> lensfun JSON fallback (10-15%) -> manual entry (remainder)

Files created:
- `research_web_app_apis/overview.md`
- `research_web_app_apis/geocoding_comparison.md`
- `research_web_app_apis/sensor_size_approaches.md`
- `research_web_app_apis/recommendations.md`

### Prompt 4 (2026-03-17) -- Deployment platform research

Comprehensive research into deployment strategies for a Python backend (FastAPI, Docker, ~1GB image) + JS frontend (Svelte/Vue SPA) web app, with focus on GitHub Student Developer Pack credits.

Platforms evaluated:
- Frontend: Vercel, Netlify, GitHub Pages, Render static, DigitalOcean App Platform
- Backend: Render, Heroku, DigitalOcean, Fly.io, Railway
- Combo: Render (both), DO App Platform (both), Heroku (both)

Key findings:
- 512 MB RAM tiers (Render Free, Heroku Basic) are risky for our dep stack -- astropy+scipy+numpy alone use ~300-400 MB
- DigitalOcean's $200 student credit is the best value: 8-12 months of comfortable hosting (1-2 GiB RAM)
- Heroku's $13/mo credit lasts 24 months but only covers 512 MB dynos
- Vercel free tier is the clear winner for frontend hosting (zero-config, CDN, preview deploys)
- Fly.io is the best long-term backend option after student credits expire (auto-stop, $5-11/mo)
- Monorepo structure recommended (frontend/ + backend/ + .github/workflows/)
- Name.com `.dev` domain recommended over Namecheap `.me`

Top recommendation: Vercel (frontend, free forever) + DigitalOcean App Platform (backend, $25/mo covered by $200 credit) + `analemma.dev` from Name.com. Migrate backend to Fly.io when credit runs out.

Files created:
- `research_deployment/overview.md`
- `research_deployment/frontend_hosting.md`
- `research_deployment/backend_hosting.md`
- `research_deployment/combo_hosting.md`
- `research_deployment/ci_cd_and_repo_structure.md`
- `research_deployment/recommendations.md`

### Prompt 3 (2026-03-17) -- Licensing research (MIT code + CC images)

Researched licensing considerations for releasing the project under MIT while including CC-licensed Wikimedia Commons images. Central question: does the analemma overlay create a "derivative work" under CC BY-SA 4.0, and if so, what are the obligations?

Key findings:
- MIT code + CC images coexist fine in multi-license repos. Different licenses apply to different files. No conflict.
- The analemma overlay almost certainly constitutes an "adaptation" (derivative work) under CC definitions. The output image is "based on" the original and adds new visual elements requiring copyright permission.
- For CC BY-SA inputs, the overlaid output must be labeled CC BY-SA 4.0. This does NOT affect the code license -- MIT stays MIT.
- For CC BY inputs (cold_canada, sharjah_sands), the output just needs attribution and a modification note. No ShareAlike.
- For CC0 (hunan), no obligations at all.
- The unlicensed personal photos (nigeria, raghav*, robert_hawaii) are the biggest risk -- need explicit permission or removal from public repo.
- Web display = distribution under CC terms. Attribution must be visible where images appear.
- A basic Terms of Service is needed for the web app covering user uploads, content ownership, and storage policy.
- The repo as a whole is a "collection" (not an adaptation), so MIT can cover the collection while each image retains its own license.

Files created:
- `research_licensing/overview.md`
- `research_licensing/sharealike_analysis.md`
- `research_licensing/license_details.md`
- `research_licensing/attribution_guide.md`
- `research_licensing/repo_structure.md`
- `research_licensing/web_display_and_uploads.md`

### Prompt 2 (2026-03-17) -- Frontend framework research

Detailed comparison of six frontend approaches for the Analemma Engine web UI: React+Vite, Next.js, Vue 3+Vite, Svelte/SvelteKit, Vanilla JS+Alpine.js/HTMX, and Astro. Evaluated each against learning curve, bundle size, image upload handling, mobile responsiveness, animation capabilities (critical for the animated figure-8 visualization), ecosystem breadth, deployment, and community.

Key findings:
- Svelte/SvelteKit is the top recommendation -- built-in `draw` transition is tailor-made for SVG path animation of the analemma curve, smallest bundles, lowest learning curve
- Vue 3 is the strong runner-up -- gentler than React, larger ecosystem than Svelte, VueUse composables are very useful
- React is the safe default but carries unnecessary complexity for this single-page tool
- Next.js is overkill (SSR/server components wasted on a static SPA)
- Alpine.js/HTMX lacks animation capabilities needed for the figure-8 visualization
- Astro is wrong tool -- designed for content sites, not interactive tools
- Tailwind CSS recommended for styling regardless of framework choice
- Nominatim (OpenStreetMap) recommended for free geocoding autocomplete
- exifr recommended for EXIF parsing; heic2any for HEIC conversion

Files created:
- `research_frontend_frameworks/overview.md`
- `research_frontend_frameworks/detailed_comparison.md`
- `research_frontend_frameworks/recommendations.md`
- `research_frontend_frameworks/ecosystem_notes.md`

### Prompt 1 (2026-03-17) -- Backend framework research

Conducted a detailed comparison of five Python web frameworks (FastAPI, Flask, Django, Starlette, Litestar) for serving the Analemma Engine as a web API. Research covered setup complexity, file upload handling, async/CPU-bound concurrency patterns, binary image responses, CORS, deployment, Docker containerization with heavy scientific packages, and task queue architecture.

Key findings:
- FastAPI is the recommended framework -- good file upload handling, auto-generated Swagger docs, Pydantic validation, and a clear path for CPU-bound work via ProcessPoolExecutor
- For V1, simple Uvicorn multiprocess workers (--workers 4) are sufficient -- no Celery/Redis needed
- Docker images will be 800MB-1GB due to astropy/scipy/numpy; use python:3.12-slim with multi-stage builds
- Render or Fly.io are the best deployment targets for this project size
- pandas, plotly, and possibly matplotlib can be dropped from the API requirements to save ~115MB

Files created:
- `research_backend_framework/overview.md`
- `research_backend_framework/framework_comparison.md`
- `research_backend_framework/concurrency_and_task_queues.md`
- `research_backend_framework/docker_and_deployment.md`
- `research_backend_framework/recommendation.md`

---

## Session 2 -- started 2026-03-17

### Prompt 1 (2026-03-17) -- Research agent creation

Created a general-purpose Research agent (`research.agent.md`) at the user profile level so it's available across all workspaces. The agent's job: investigate implementation technologies, compare approaches, and produce structured markdown research in `research_{topic}/` directories at the workspace root. It uses web search, Context7 MCP, and codebase reading, then writes findings into separate .md files per sub-topic.

Key design choices:
- User-level placement for cross-project reuse
- Tools: read, search, edit, web, todo, agent (no terminal -- research only)
- Can edit project docs (README, implementation notes) but never source code
- Moderate question frequency -- asks user at meaningful decision forks, not every minor choice
- Falls back to plan-agent behavior for non-research tasks

Files created:
- `%APPDATA%/Code/User/prompts/research.agent.md`

---

## Session 1 -- started 2026-03-15

### Prompt 6 (2026-03-17) -- CV simplification

Reverted the sun detection algorithm from Gaussian-blur-based center finding back to simple brightness-weighted centroid for all blob sizes. The Gaussian blur approach (Rounds 10-13 in CV_debugging.md) was tuned for three difficult images (cold_canada, russia_meadow, brofjorden) but shifted detection off-center for mainstream images with large overexposed blobs -- hongkong, raghav, raghav2, and others.

The simplified algorithm keeps progressive thresholding (0.999 -> 0.96, min 20px blob) and uses weighted centroid for all blobs regardless of size. No large-blob vs small-blob branching, no Gaussian blur, no adaptive sigma. This proved more robust across all 11 test images.

Files changed:
- Modified: `analemma/image_anchor.py` (removed Gaussian blur path, unified to weighted centroid)
- Modified: `docs/TECHNICAL_DESCRIPTION.md`, `docs/THEORY_AND_LIMITATIONS.md` (updated sun detection descriptions)
- Modified: `docs/PROJECT_LOG.md`
- Regenerated: all 11 output overlay sets

---

### Prompt 5 (2026-03-17) -- Final cleanup

Reran the engine for all 11 images to regenerate output overlays, sky charts, and composites. Cleaned every output folder down to exactly 3 files each. Removed `output/quickstart_output/`, `output/visualizations/`, and `output/README.md`.

Removed legacy demo scripts: `quickstart.py`, `show_detection.py`, `test_hongkong.py`, `test_nigeria.py`, and `demo_scripts/README.md`. Only `process_image.py` remains.

Rewrote `.gitignore` to track all input images and output files except private ones (raghav, raghav2, raghav6, robert_hawaii). Removed the blanket `output/`, `input_images/`, and `**/*.png` rules.

Added hongkong overlay as the README example image.

Updated copilot-instructions.md with the full writing style rule (no em-dashes, no emoji, no "**Topic:** description" format, no AI giveaways).

Rewrote docs: STRUCTURE.md (was referencing deleted files), USAGE_GUIDE.md (was referencing quickstart.py and listing astropy/scipy as optional), THEORY_AND_LIMITATIONS.md (sun detection section was outdated), TECHNICAL_DESCRIPTION.md (updated sun detection algorithm to match Round 13, removed dummy from validation table, updated 11 test datasets, fixed timezone section, updated dependencies as all required, removed bold-colon patterns).

Restructured this PROJECT_LOG from 4 separate "sessions" into a single session with prompt-numbered entries.

Files changed:
- Modified: `.gitignore`, `README.md`, `.github/copilot-instructions.md`
- Modified: `docs/STRUCTURE.md`, `docs/USAGE_GUIDE.md`, `docs/TECHNICAL_DESCRIPTION.md`, `docs/THEORY_AND_LIMITATIONS.md`
- Modified: `docs/PROJECT_LOG.md`, `docs/IMPLEMENTATION_NOTES.md`
- Deleted: `demo_scripts/quickstart.py`, `demo_scripts/show_detection.py`, `demo_scripts/test_hongkong.py`, `demo_scripts/test_nigeria.py`, `demo_scripts/README.md`
- Deleted: `output/quickstart_output/`, `output/visualizations/`, `output/README.md`
- Deleted: fluff files from all output folders (old approximate/HP overlays, detection images, PDFs, final composites)
- Regenerated: all 11 output overlay sets via `process_image.py`

---

### Prompt 4 (2026-03-17) -- CV debug cycle, coordinate parser, cleanup start

**CV Sun Detection -- 13-Round Debug Cycle**

The auto-detection algorithm (`_detect_sun_position()` in `image_anchor.py`) went through 13 rounds of iterative refinement across four problem images: cold_canada, russia_meadow, brofjorden, and hongkong. Full technical history is in `docs/CV_debugging.md`.

Final algorithm (Round 13):
1. Progressive thresholding: starts at 0.999, lowers through 0.96 until a blob >= 20px is found
2. Large blobs (>100px): Gaussian blur on sum-of-channels luminance within cropped bbox; sigma = `max(1, min(blob_radius * 0.12, 5))`
3. Small blobs (<=100px): weighted centroid using gray intensity
4. Fallback: brightest pixel if no blob found

Key findings:
- cold_canada had a single glare pixel at (928,437) reaching max brightness -- progressive thresholding correctly skips it (too small)
- cold_canada's real sun blob (411px at 0.96 threshold) is uniformly saturated (244-246 across all channels). No gradient exists to locate a true center. Detection at (750,235) is as good as possible.
- Sigma cap was critical: capping at 8 broke hongkong/raghav/raghav2 (massive blobs get over-smoothed); capping at 5 restored them while preserving cold_canada and russia_meadow
- russia_meadow approved at (570,335); brofjorden accepted at (1052,347)
- EXIF orientation (`exif_transpose`) matters: hongkong rotates from 3456x2592 to 2592x3456

Diagnostic results (all images, Round 13):

| Dataset | Sun Pixel | Blob Size | Notes |
|---------|-----------|-----------|-------|
| hongkong | (917, 372) | 163753px | Restored with sigma=5 cap |
| robert_hawaii | (598, 700) | -- | Stable |
| nigeria | (629, 454) | -- | Stable |
| raghav | (2433, 915) | 38144px | Restored with sigma=5 cap |
| raghav2 | (1108, 348) | 54675px | Restored with sigma=5 cap |
| raghav6 | (3388, 451) | -- | Stable |
| sharjah_sands | (598, 388) | -- | Stable |
| hunan | (504, 136) | -- | Stable |
| cold_canada | (750, 235) | 411px | Saturated blob, accepted |
| russia_meadow | (570, 335) | -- | Approved |
| brofjorden | (1052, 347) | -- | Accepted |

**Metadata Parser -- Flexible Coordinate Formats**

Added `parse_coordinate()` to `metadata_parser.py`. Handles plain decimal, decimal with direction (2.2945E, 40.1N), and DMS with symbols (8 deg 48' 26.98" E). All existing metadata files still parse identically.

Also deleted `input_images/dummy/` entirely and removed its notebook cell.

Files changed:
- Modified: `analemma/image_anchor.py` (Round 13: progressive threshold + adaptive sigma capped at 5)
- Modified: `analemma/metadata_parser.py` (added `parse_coordinate()`)
- Modified: `docs/METADATA_REFERENCE.md` (documented flexible coordinate formats)
- Created: `docs/CV_debugging.md`
- Deleted: `input_images/dummy/`

---

### Prompt 3 (2026-03-17) -- IANA timezone, scipy, horizon cutoff, spurious lines

1. Replaced `round(longitude/15)` timezone detection with `timezonefinder` + `zoneinfo` for proper IANA lookup. Three-tier fallback: explicit > IANA auto > round(lon/15). Correctly handles DST (UIUC Sep = UTC-5 CDT), half-hour offsets (India = UTC+5.5), and political boundaries (Hawaii = UTC-10). Added `reference_datetime` parameter to `SkyMapper` for DST-aware detection.

2. Installed scipy -- root cause of all CV sun detection failures. Without scipy, `_detect_sun_position()` fell back to simple brightest-pixel averaging.

3. Removed horizon cutoff from `generate_analemma_points()`. All 365 points are now computed; only image bounds constrain visibility. Sharjah sands overlay now correctly shows analemma extending below horizon.

4. Fixed spurious overlay lines. Segment-based line drawing breaks the polyline at out-of-bounds gaps (raghav6 fix).

5. Switched all notebook cells to high-precision mode as default.

6. Created `docs/THEORY_AND_LIMITATIONS.md`.

7. Moved `IMPLEMENTATION_NOTES.md` and `PROJECT_LOG.md` into `docs/`.

Files changed:
- Modified: `analemma/sky_mapper.py`, `analemma/image_anchor.py`, `analysis.ipynb`, `requirements.txt`
- Created: `docs/THEORY_AND_LIMITATIONS.md`

---

### Prompt 2 (2026-03-16) -- Bug fixes, TECHNICAL_DESCRIPTION rewrite

Fixed all 3 critical bugs identified in Prompt 1:

1. Timezone auto-detection: added `timezone_offset` parameter to `SkyMapper` and `ImageAnchorer`, added `TIMEZONE_OFFSET` field to metadata parser. Added `TIMEZONE_OFFSET=-10` to robert_hawaii metadata.

2. HP EoT fallback: replaced the approximate EoT call in `calculate_high_precision()` with a proper Astropy-based EoT using mean solar longitude $L_0$ and Astropy's sun RA. Initially had a sign error; corrected to NOAA convention. Mode comparison now shows max EoT diff = 5.3 min, max dec diff = 1.2 deg.

3. Linear image projection: added `cos(mean_altitude)` correction to `sky_to_pixel()`. At the Hawaii anchor altitude of ~48 deg, horizontal offsets were ~33% too large.

Also created `.github/copilot-instructions.md`, `IMPLEMENTATION_NOTES.md`, and added diagnostic cells for all remaining images (Nigeria, Raghav, Raghav2, Raghav6, Sharjah Sands). Rewrote `TECHNICAL_DESCRIPTION.md` from scratch.

Known DST limitation identified: Oregon auto-detected as UTC-8 (PST) but photo datetime was during PDT (UTC-7). Fixed in Prompt 3 with IANA detection.

Files changed:
- Modified: `analemma/calculator.py`, `analemma/sky_mapper.py`, `analemma/image_anchor.py`, `analemma/metadata_parser.py`
- Modified: `analysis.ipynb`, `docs/TECHNICAL_DESCRIPTION.md`
- Created: `.github/copilot-instructions.md`, `IMPLEMENTATION_NOTES.md`

---

### Prompt 1 (2026-03-15) -- Initial audit, notebook, bug discovery

Comprehensive project review of all docs and core source files. Launched a subagent code audit checking mathematical accuracy, code quality, and bugs.

Moved PROJECT_BRIEF.md, TECHNICAL_DESCRIPTION.md, USAGE_GUIDE.md, METADATA_REFERENCE.md, STRUCTURE.md into `docs/`.

Created `analysis.ipynb` with import cell, helper function `process_and_display()`, Hong Kong cell, Robert Hawaii cells, timezone diagnostic cell, and mode comparison cell.

Bugs found:

| # | Bug | Severity | Module |
|---|-----|----------|--------|
| 1 | Timezone auto-detection wrong for Hawaii: `round(-157.8/15) = -11`, actual -10 | CRITICAL | sky_mapper.py |
| 2 | HP EoT falls back to approximate formula | CRITICAL | calculator.py |
| 3 | Image projection missing cos(altitude) correction | CRITICAL | image_anchor.py |
| 4 | No timezone field in metadata parser | MODERATE | metadata_parser.py |
| 5 | Declination approximation ~1.2 deg max error | MINOR | calculator.py |

Files changed:
- Created: `analysis.ipynb`, `PROJECT_LOG.md`
- Moved to `docs/`: PROJECT_BRIEF.md, TECHNICAL_DESCRIPTION.md, USAGE_GUIDE.md, METADATA_REFERENCE.md, STRUCTURE.md
