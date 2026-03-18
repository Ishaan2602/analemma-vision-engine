# Analemma Project -- Implementation Notes

Technical details, theory explanations, and answers to implementation questions. Most recent at the top.

---

## Session 4 -- continued (2026-03-18): Feature Batch

### Text naturalization approach

The About and Methodology pages were rewritten to avoid common AI-generated patterns. Specific changes: reduced double-hyphen (em-dash substitute) usage from ~15 instances per page to 0-2, converted bulleted "Topic: description" lists into flowing paragraphs where the structure didn't add clarity (particularly in Limitations), varied paragraph length so not every block is 2-3 sentences, removed summarizing sentences that just restated what the preceding paragraph already said, and let some sections end without a neat concluding thought. The Methodology page kept its numbered structure and formula blocks since those are genuinely useful for scannability.

### Charts endpoint design

The /api/charts endpoint only takes lat/lon/datetime -- no image upload needed. Sky chart and figure-8 are purely astronomical plots generated from the engine's AnalemmaPlotter. matplotlib uses the Agg backend to avoid GUI display issues in Docker. Charts are rendered at 150 DPI to BytesIO buffers, base64-encoded, and returned as JSON. Figures are explicitly closed after encoding to prevent memory leaks in the long-running server process.

### Sun picker coordinate mapping

SunPicker displays the image scaled to fit the viewport (max-h-[70vh] object-contain). When the user clicks, pixel coords are computed as: `(click offset from image edge) / (displayed size) * (natural image dimension)`. This gives coordinates in the original image's pixel space, which is what the backend expects for sun position. The marker position is tracked in both natural (for data) and display (for visual positioning) coordinates.

### Detection failure flow

When /api/analyze returns an error containing "sun" and "detect" (case-insensitive), the app sets `detectionFailed = true` which: (1) shows an amber error banner with guidance, (2) auto-expands the Sun Position section in MetadataForm, (3) shows a warning inside that section. The user can then click "Select sun position on image" to open the SunPicker modal, pick the sun, and retry generation with explicit coordinates.

### Tab navigation with $app/state

SvelteKit 2.50+ exposes `page` from `$app/state` as a Svelte 5 rune (not a store). Used `page.url.pathname` directly in template expressions for active tab highlighting. The mobile nav renders below the header; desktop nav sits inline next to the title.

---

## Session 4 -- continued (2026-03-18): Rendering Fixes

### Investigation Summary

Six issues were reported after initial deployment. Root causes traced below.

### 1. Wrong analemma curves for sample images (hongkong, russia_meadow, etc.)

Root cause: the frontend fetches 400px-wide JPEG thumbnails and sends them to the backend as the "image." The engine auto-detects the sun by finding the brightest pixel region. On a 400px compressed JPEG, JPEG artifacts and resolution loss cause the sun detection to land on a completely different pixel than on the original. Since the entire analemma curve is plotted relative to the anchor pixel, a shifted sun = a shifted curve.

Additional issue for hongkong: the original JPEG has EXIF orientation tag (rotation). The engine calls `ImageOps.exif_transpose()` which rotates the original from 3456x2592 landscape to 2592x3456 portrait. But the thumbnail generation script didn't apply EXIF transpose before resizing, so the thumbnail is 400x300 landscape -- wrong aspect ratio, wrong orientation. The engine then calculates everything in landscape when the photo is actually portrait.

Fix: three changes working together.
- Regenerate thumbnails at 1200px wide with EXIF transpose applied first and quality 90.
- Pre-compute each sample's sun pixel on the full-res original, scale proportionally to the 1200px thumbnail dimensions, and store as `sun_x`/`sun_y` in the sample metadata.
- Frontend sends `sun_x`/`sun_y` with the FormData when a sample is selected. This bypasses auto-detection entirely, so the analeamma anchors to the correct pixel.

### 2. raghav2 produces a different analemma than expected

False alarm -- the user had entered wrong metadata while testing (35mm-equivalent focal length instead of actual). With correct metadata, raghav2 produces the right output. No code changes were made for this issue.

### 3. Connecting line drawn across image when analemma is cut off

Root cause: the SVG path is built as a single continuous polyline -- `M x,y L x,y L x,y...` -- from all in-bounds points sorted chronologically. When the analemma goes out of bounds at one part of the figure-8 and re-enters at a distant point, the single path draws a straight line across the image connecting those distant points.

Fix: detect gaps and break the path. Consecutive in-bounds points that are far apart (distance > some threshold based on the typical spacing) start a new `M` (moveTo) instead of `L` (lineTo). This produces multiple disjoint path segments with no spurious connecting lines. Same approach the backend engine uses in `overlay_analemma()`.

### 4. Low-quality sample images

Root cause: thumbnails were generated at 400px wide, JPEG quality 85, giving 7-20KB files. At this resolution the image looks noticeably blurry in the viewer, especially on desktop.

Fix: regenerate at 1200px wide, quality 90. File sizes increase to roughly 50-150KB each (still small), but the visual quality improves substantially.

### 5. SVG overlay lines and dots too thick

The current sizing formulas were designed for rough visual impact but produce thicker strokes than the backend engine's PIL rendering. For a 1200px-wide image, `dotRadius = max(3, min(8, 1200/500)) = 3px` which is OK, but the stroke is also relatively thick.

Fix: tighten the scaling formulas. Reduce dot radius range to 2-5px and stroke width to 1-2px to match the backend engine's subtler style.

### 6. No save option on mobile

The download button calls /api/render to get a PNG, then creates a temporary `<a>` element with `download` attribute and clicks it programmatically. Some mobile browsers (especially iOS Safari) block or ignore programmatic download clicks.

Fix: add a client-side "Save Image" button that renders the SVG + underlying image to a `<canvas>`, converts to PNG blob, and opens it in a new tab via `window.open(blobUrl)`. This works universally on mobile -- the user can then long-press the image to save it. This also avoids an extra round-trip to the backend.

---

## Session 4

### SVG overlay animation approach

The analemma overlay uses native SVG animation rather than Svelte transitions for the path draw effect. The path's `strokeDasharray` and `strokeDashoffset` are animated via `requestAnimationFrame` with `cubicInOut` easing from Svelte's easing module. This gives smoother control than CSS transitions and avoids FLIP animation complexity.

The dots use SVG `<animate>` elements with staggered `begin` times (starting at 3s, each dot delayed by 15ms), so they appear to "pop in" after the path finishes drawing. Date labels fade in at 4.5s. The anchor point (photo datetime) is highlighted red with a white stroke.

For hover tooltips, we translate mouse coordinates to SVG viewBox coordinates using the container's bounding rect and the image dimensions ratio, then find the nearest point within a 2% threshold.

### ProcessPoolExecutor for engine calls

The analemma engine (Astropy + JPL DE440 ephemeris) is CPU-bound and takes 2-10 seconds per calculation. Using `asyncio.run_in_executor` with `ProcessPoolExecutor(max_workers=2)` prevents blocking the FastAPI event loop. The worker limit of 2 is conservative for a single-container deployment -- each worker loads the full JPL ephemeris into memory (~30MB).

Temp files are used to pass images to the engine (which expects file paths, not bytes). Cleanup happens in `finally` blocks to prevent disk buildup.

### Three-tier sensor detection

The sensor size (needed for field-of-view calculation) is detected through three tiers, in priority order:

1. **EXIF crop factor**: If both `FocalLength` and `FocalLengthIn35mmFormat` exist in EXIF, the crop factor is `35mm / actual`. Combined with aspect ratio detection from image dimensions, this gives sensor width and height. Most cameras write these fields.

2. **Lensfun database lookup**: If Tier 1 fails (e.g., one focal length field is missing), we look up the camera make + model in a JSON file derived from the Lensfun project's camera database. The JSON maps `"make model"` (lowercased) to `{cropfactor, maker, model}`. A partial match fallback handles model variations.

3. **Manual entry**: The user types sensor dimensions directly. Default placeholder values guide toward common sizes.

---

## Session 3

### Why a monorepo with frontend/ and backend/ instead of separate repos

For a solo developer, a single repo is strictly better. You get atomic commits across frontend and backend, one set of issues/PRs, and one `git clone` for local dev. Every major deployment platform (Vercel, Render, DigitalOcean, Fly.io) supports monorepos with per-directory build configuration.

The engine code lives in `backend/analemma/` (copied from root) for Docker build context isolation. The root-level `analemma/` stays for CLI/notebook usage. This duplication is a V1 tradeoff -- long-term, packaging the engine as a pip-installable library (via pyproject.toml) eliminates the copy.

### Why the overlay likely counts as a derivative under CC BY-SA

The CC BY-SA 4.0 legal code defines "Adapted Material" as material "derived from or based upon the Licensed Material" that is "translated, altered, arranged, transformed, or otherwise modified." The analemma overlay adds new visual elements (the figure-8 curve, dots, labels) to the original photograph, creating a new combined image. Under most copyright frameworks, this constitutes a derivative/adaptation.

Critical distinction: the **code** is not a derivative of the images (MIT stays MIT). Only the **output images** -- the photo with the overlay baked in -- inherit the input image's license obligations. For CC BY-SA inputs, the overlaid output must be released under CC BY-SA 4.0 with proper attribution. For CC BY inputs, any license works but attribution is still required. For CC0 inputs, no restrictions.

### Why "both JSON + PNG" endpoints instead of one

For the web app, the frontend needs raw coordinate data (JSON) to render the animated SVG overlay. But users also want a downloadable static PNG. These are fundamentally different outputs from the same computation.

The JSON endpoint returns the analemma curve as an array of `{pixel_x, pixel_y, date, altitude, azimuth}` points. The frontend uses this for the animated SVG path. The PNG endpoint wraps the existing `overlay_analemma()` method. Both share the same computation chain (AnalemmaCalculator -> SkyMapper -> pixel mapping), so the API layer can compute once and serve both formats.

### Why exifr over exif-js for client-side EXIF extraction

exif-js (2.3.0) hasn't been updated since 2017 and can't parse HEIC containers at all -- it only handles JPEG and TIFF. It also loads all EXIF data into memory with no way to selectively parse specific tags.

exifr (7.1.3) parses JPEG, HEIC, HEIF, TIFF, PNG, and AVIF. It supports selective parsing (`exifr.gps(file)` returns just GPS, `exifr.parse(file, { pick: ['FocalLength', 'Make'] })` fetches specific tags). It reads only the first ~64KB of the file by default, so parsing is near-instant even on large files. It's tree-shakeable (only import what you need), actively maintained, and has 794K weekly npm downloads.

piexifjs (1.0.6) is a read/write library focused on JPEG/TIFF only -- no HEIC. The write capability is useful for editing EXIF but we don't need that.

### Why client-side EXIF + server-side re-extraction (not just one or the other)

Client-side extraction with exifr gives instant form pre-fill -- the user uploads a photo and immediately sees coordinates, datetime, and focal length populated. No round trip to the server.

But we can't trust client-side values as the sole source. The browser environment is untrusted, and the EXIF data could be modified or fabricated before it reaches the server. The server re-extracts EXIF from the uploaded file bytes using Pillow's `getexif()` and uses those values as ground truth for the computation. Client-side values are a UX convenience; server-side values drive the engine.

This also handles the case where a user edits a pre-filled field (e.g., corrects a GPS coordinate). The server accepts form fields alongside the file, uses manual overrides when provided, and falls back to EXIF data from the file when fields are empty.

### Why SVG path animation instead of Canvas or CSS keyframes for the figure-8

The analemma curve is a smooth path through 365 discrete points. SVG's `<path>` element with `stroke-dasharray` / `stroke-dashoffset` animation is purpose-built for this: you set `dasharray` to the total path length, then animate `dashoffset` from full length to zero. The path "draws itself" progressively.

Svelte's built-in `draw` transition does exactly this with zero configuration -- just `<path transition:draw={{ duration: 2000 }} d={pathData} />`. No external animation library needed.

Canvas would require manually drawing partial paths frame-by-frame with `requestAnimationFrame`, managing the animation loop, and losing the declarative reactivity that Svelte provides. CSS keyframes can animate `stroke-dashoffset`, but you need to know the path length at build time or compute it in JS -- Svelte's `draw` handles this automatically.

GSAP is the most capable animation library (timeline sequencing, physics easing), but it's 27KB gzipped and its "free" license has commercial restrictions. For a single path animation, it's overkill.

### Why the server needs a get_analemma_json() method

ImageAnchorer currently only outputs rasterized overlays -- `overlay_analemma()` returns a PIL Image with the curve baked into the pixel data. For the web frontend to animate the curve, it needs the raw point data: pixel coordinates, dates, and solar altitude/azimuth for each point on the analemma.

`generate_analemma_points()` already computes this internally and returns a list of dicts with `pixel_x`, `pixel_y`, `date`, `altitude`, `azimuth`. A new `get_analemma_json()` method would be a thin wrapper that calls `generate_analemma_points()` and returns the result as a JSON-serializable structure. The FastAPI endpoint would return both the static overlay image and this JSON in a multipart response (or two separate endpoints).

### Deriving sensor dimensions from EXIF crop factor

Most cameras write two focal length tags into EXIF: `FocalLength` (actual, e.g. 4.25mm) and `FocalLengthIn35mmFormat` (35mm equivalent, e.g. 26mm). The ratio gives the crop factor, which encodes the sensor size relative to 35mm full frame (36x24mm, diagonal 43.27mm).

For 3:2 aspect sensors (DSLRs, mirrorless): `sensor_width = 36 / crop_factor`, `sensor_height = 24 / crop_factor`.

For 4:3 aspect sensors (most smartphones, compacts): the diagonal is `43.27 / crop_factor`, then `width = diagonal * 4/5 = diagonal * 0.8`, `height = diagonal * 3/5 = diagonal * 0.6`. This comes from the Pythagorean relationship: if aspect is w:h, then `width = diagonal * w / sqrt(w^2 + h^2)`.

The 3:2 vs 4:3 distinction matters: using the wrong formula introduces ~4% FOV error. We can detect the sensor's aspect ratio from `ImageWidth`/`ImageHeight` in EXIF (after accounting for orientation).

Lensfun's database stores only `cropfactor`, not raw sensor dimensions or aspect ratio. So we'd still need the aspect ratio detection for accurate conversion.

### Why LocationIQ over Google Places for geocoding

Google Places Autocomplete is technically superior (better data, better typo handling, better POI coverage), but its Terms of Service require that autocomplete results be displayed on a Google Map or link to a Google Maps page. We don't want a map in our UI -- we just want lat/long coordinates from a city search. Using Google's data without showing their map violates the ToS.

Same issue with Mapbox: their Geocoding API requires results to be shown on a Mapbox map. Their "Temporary Geocoding" product can't even store results.

LocationIQ, Geoapify, and MapTiler all allow using geocoding results without a map display, with simple attribution requirements. LocationIQ has the most generous free tier at 5,000 requests/day.

### Why 512 MB RAM isn't enough for the API backend

The Python dependency stack for the Analemma engine has a large memory footprint at import time. Just importing the core libraries without doing any work consumes ~480-530 MB:

- Python runtime: ~50 MB
- numpy + scipy (imported modules + BLAS): ~100 MB
- astropy + IERS data + coordinate frames: ~150 MB
- JPL DE440 ephemeris (loaded on first calculation): ~100 MB
- Pillow + an input image: ~50-100 MB
- FastAPI + Uvicorn overhead: ~30 MB

During active processing -- loading a large image, computing a year's solar positions, rendering the overlay -- peak RAM hits 700-900 MB. Any free/basic tier with 512 MB will either swap heavily (if swap exists) or OOM kill the process.

The minimum comfortable tier is 1 GiB for a single-worker deployment with dependency trimming (drop matplotlib, pandas, plotly from the API). 2 GiB gives headroom for larger images and the possibility of 2 Uvicorn workers.

### Path-based routing vs CORS for frontend-backend communication

When the frontend and backend share a domain (e.g., `analemma.dev` serves the SPA, `analemma.dev/api/process` hits the backend), the browser treats all requests as same-origin. No CORS middleware needed. This is possible when both are deployed on the same platform with routing rules (DigitalOcean App Platform, or Heroku serving static files from FastAPI).

When split across platforms (e.g., frontend on Vercel at `analemma.dev`, backend on DO at `api.analemma.dev`), the browser considers them different origins. The backend must include CORS headers allowing the frontend origin. In FastAPI this is one middleware call, but it's an extra thing to configure and debug.

### Why the analemma overlay is (probably) a derivative work under CC BY-SA

CC BY-SA 4.0 defines "Adapted Material" as material "derived from or based upon the Licensed Material and in which the Licensed Material is translated, altered, arranged, transformed, or otherwise modified in a manner requiring permission under the Copyright and Similar Rights."

The CC FAQ says a modification rises to the level of adaptation when it's "based on the prior work but manifests sufficient new creativity to be copyrightable."

The overlay adds a calculated figure-8 curve, date markers, and annotation to an existing photograph. The original photo is reproduced in full. The resulting combined image couldn't exist without the original. Under most copyright frameworks (especially U.S. law's low originality threshold), this creates a derivative.

The counter-argument -- that the photo is just a "background" for data visualization, like pinning a chart on a map -- is plausible but weaker. The conservative and safer interpretation is: it's a derivative.

Critical implication: this only affects **output images**, not the **code**. The code that produces derivatives isn't itself a derivative of the images, just like Photoshop isn't a derivative of every photo edited with it. MIT stays MIT. Only the output images with CC BY-SA inputs need to carry CC BY-SA 4.0.

### Why the repository isn't "infected" by ShareAlike

The repo is a collection (code + sample images), not an adaptation. The CC FAQ explicitly says collections can use any license while individual items retain their own licenses: "You may choose a license for the collection, however this does not change the license applicable to the original material." ShareAlike only triggers on adaptations, not collections.

### Why FastAPI over Flask for a CPU-bound image processing API

The conventional wisdom is "Flask is simpler, use it for small projects." That's true for trivial APIs, but our use case has specific requirements that tilt toward FastAPI:

1. **File upload typing.** FastAPI's `UploadFile` parameter with `Form(...)` metadata fields gives us validated multipart parsing with zero boilerplate. Flask's `request.files` works but requires manual validation for every field.

2. **Swagger UI for free.** During development, auto-generated docs at `/docs` let you test the upload endpoint from a browser without building a frontend. With Flask, you'd need to write curl commands or build a test page.

3. **Async option available but not required.** For V1, use plain `def` handlers (FastAPI runs them in a threadpool automatically). If we later need async (cloud storage, external APIs), we don't need to restructure -- just change `def` to `async def`.

4. **CPU-bound work in both frameworks.** Neither Flask nor FastAPI "solve" CPU-bound concurrency. Flask uses Gunicorn multiprocess workers; FastAPI uses Uvicorn multiprocess workers. Both give you N-workers = N-concurrent-computations. The frameworks are equivalent here.

The overhead of FastAPI over Flask is one extra dependency (Pydantic) and slightly different syntax. The payoff is validation, documentation, and a cleaner async upgrade path.

### Why not Celery/Redis for V1

The Analemma computation takes 3-10 seconds. That's within normal HTTP timeout windows (browsers default to 60-120 seconds). Adding Celery means:
- A Redis or RabbitMQ server to run and manage
- Docker Compose goes from 1 container to 3
- Result storage (where does the 10MB processed image live between completion and client fetch?)
- A polling API on the client side

None of this is justified until you're seeing sustained concurrent load that overwhelms the worker pool. With 4 Uvicorn workers on a 2-core machine, you can handle 4 simultaneous users. If user #5 shows up, they wait a few seconds in the Uvicorn connection queue. That's fine for moderate traffic.

### Docker image size with scientific Python

astropy + scipy + numpy + matplotlib + Pillow = ~270MB of Python packages before you count the JPL DE440 ephemeris (~100MB). The full stack pushes images past 1GB. Key mitigations:
- Use `python:3.12-slim` (not alpine -- numpy/scipy wheels don't work on musl libc)
- Multi-stage build to exclude build tools from runtime image
- Pre-download ephemeris data during build so it doesn't happen at runtime
- Drop pandas/plotly if the API doesn't need them (the notebook does, but the API doesn't)

---

## Session 1

### Prompt 4 (2026-03-17)

### Why sigma capping matters for sun detection

The Gaussian blur sigma controls how much smoothing is applied when finding the brightness peak within a sun blob. For small blobs (radius ~11px like cold_canada), you want a tight sigma (~1.4) to accurately find the peak. For large blobs (radius 100-230px like hongkong/raghav), sigma=5 works well -- it smooths out noise without pulling the peak too far from the true center.

The adaptive formula `sigma = max(1, min(blob_radius * 0.12, cap))` was the solution. With cap=8, large blobs (hongkong: radius=228) got sigma=8, which over-smoothed and shifted the detection by 20+ pixels. With cap=5, those blobs get the same sigma=5 that was proven in Round 10, while cold_canada's small blob gets sigma=1.37 (well under the cap).

### Why cold_canada can't be improved further

cold_canada's sun blob at the 0.96 detection threshold contains 411 pixels with RGB values ranging only from 244 to 246 across all three channels. The entire blob is uniformly saturated to near-white. No weighting scheme (luminance, whiteness, centroid) can distinguish a meaningful center within this flat region. Different Gaussian sigma values shift the peak by a few pixels, but all are equally valid. The detection at (750, 235) is as good as any algorithm can achieve on this data.

### Coordinate parsing implementation

`parse_coordinate()` uses a two-pass approach:
1. Strip trailing direction letter (N/S/E/W) if present
2. Try parsing as a plain decimal (removing any trailing degree symbol)
3. If that fails, split on DMS separators (degree signs, prime marks, spaces, d/m/s letters) and convert degrees + minutes/60 + seconds/3600
4. Apply sign from direction letter (S and W → negative)

This covers everything from `40.1` to `8° 48' 26.98" E` without requiring users to standardize their format.

---

### Prompt 3 (2026-03-17)

#### Timezone rework: IANA database auto-detection

Replaced the `round(longitude/15)` timezone detection with a proper IANA database lookup using `timezonefinder` + Python's built-in `zoneinfo`. The new system:

- Detects IANA timezone name from (lat, lon) using `TimezoneFinder`
- Uses `ZoneInfo` to compute the exact UTC offset for the given reference datetime, correctly handling DST and half-hour offsets
- Three-tier fallback: explicit `timezone_offset` parameter > IANA auto > `round(lon/15)` with warning
- Added `reference_datetime` parameter to `SkyMapper.__init__()` for DST-aware detection
- Added `_iana_timezone_name` attribute to `SkyMapper` for diagnostics

Verified correct detection for 9 locations:
- Hawaii: -10 (was -11), Hong Kong: +8, Nigeria: +1, UIUC Sep: -5 (CDT), Oregon Jun: -7 (PDT), Houston Jan: -6 (CST), Sharjah: +4, W. China: +6, India: +5.5

#### scipy installed -- CV sun detection now functional

Root cause of all CV sun detection failures across images (hongkong, nigeria, raghav): `scipy` was not installed in the virtual environment. Without scipy, the `_detect_sun_position()` method fell back to simple brightest-pixel averaging, which fails with lens flare, reflections, and overexposed regions.

With scipy installed (v1.17.1), the pipeline now uses connected-component labeling (`ndimage.label`) to find the largest bright blob and computes its brightness-weighted center of mass.

#### Removed horizon cutoff from overlay

`generate_analemma_points()` in `image_anchor.py` previously filtered points with `altitude < 0`. This was removed -- all 365 points now have pixel coordinates computed. The image bounds are the only constraint on which points appear in the overlay. This correctly shows the analemma extending below the horizon (e.g., Sharjah sands, where the analemma dips to -16.6 deg altitude but the camera captures terrain below the horizon line).

#### Fixed spurious line in raghav6 overlay

The old `overlay_analemma()` drew a single continuous polyline through ALL in-bounds points. When a gap of out-of-bounds points separated two visible segments, the line jumped across the gap. Fixed by implementing segment-based line drawing: the line breaks whenever a point falls outside image bounds, preventing connections between non-adjacent visible points.

#### Other changes

- Default mode in `process_and_display()` changed from `'approximate'` to `'high-precision'`.
- Cell 11 (timezone diagnostic) rewritten to test IANA detection for 9 locations with fixed axes comparison.
- Created `docs/THEORY_AND_LIMITATIONS.md`.
- Added `scipy>=1.10.0` and `timezonefinder>=6.0.0` to requirements.txt.

#### Why does a near-zenith overlay appear "slim" while the sky chart appears "fat"?

At high altitude (~70 deg), `cos(70 deg) = 0.34`, meaning 1 degree of azimuth maps to only 0.34 degrees of apparent angular separation. The sky chart plots azimuth in true degrees (appearing wide), while the overlay correctly applies the cosine compression (appearing narrow). Physically correct behavior, not a bug. See `docs/THEORY_AND_LIMITATIONS.md` Section 5.1 for the full explanation.

#### Why was the Robert Hawaii small loop appearing too large in the overlay?

With the old timezone (UTC-11 instead of UTC-10), the anchor altitude was ~48 deg instead of ~34 deg. The `cos(altitude)` compression was stronger at 48 deg, making the loop appear differently sized compared to the sky chart. With correct timezone (UTC-10), the anchor altitude is ~34 deg and the overlay matches the sky chart proportions better.

---

### Prompt 2 (2026-03-16)

#### Why doesn't default timezone auto-detection handle DST?

The auto-detection formula `round(longitude/15)` produces the **standard time** offset for the longitude band. It has no concept of Daylight Saving Time because DST is a political/legal convention that varies by country, state, and even county.

For example, Oregon at longitude -122.6 auto-detects as UTC-8 (PST). But on June 1, Oregon observes PDT (UTC-7). If the photo's datetime field records the local clock time (13:45 PDT), using UTC-8 instead of UTC-7 introduces a 1-hour (15-degree azimuth) error.

Workaround: users in DST regions should set `TIMEZONE_OFFSET` in metadata to match the UTC offset of their clock at the time the photo was taken. For Oregon in summer: `TIMEZONE_OFFSET=-7`. (This was properly fixed in Prompt 3 with the IANA timezone system.)

#### What does the HP EoT sign convention mean?

The NOAA convention is: **EoT = apparent solar time - mean solar time**. Equivalently, EoT = (mean sun RA - true sun RA) in time units.

- **EoT > 0**: The true sun is *ahead* of the mean sun. Solar noon occurs *before* 12:00 clock time. The sun is further west than expected for the clock time.
- **EoT < 0**: The true sun is *behind* the mean sun. Solar noon occurs *after* 12:00 clock time.

In our implementation: `EoT_minutes = (L0/15 - RA_sun_hours) * 60`, where `L0` is the mean solar longitude. This is equivalent to the NOAA definition because `L0/15` gives the mean sun's RA in hours (modulo the small difference between ecliptic longitude and RA for the mean sun, which averages out over the year).

#### Why do we need TIMEZONE_OFFSET in metadata?

The recorded datetime in a photo's EXIF data (and therefore in our `metadata.txt`) is the **local clock time** at the moment of capture. The analemma calculation needs to convert this clock time into a **solar hour angle** -- the angular position of the sun relative to the observer's meridian. This conversion requires knowing the relationship between the local clock and UTC:

```
Hour Angle = (clock_time - 12:00) * 15 deg/hr + EoT/4 + (longitude - timezone_meridian)
```

The term `timezone_meridian = timezone_offset * 15` defines the "center longitude" that the local clock is synchronized to. The difference `longitude - timezone_meridian` corrects for the observer not being exactly on that meridian.

Auto-detection fails because the naive formula `round(longitude / 15)` assumes timezones are perfectly aligned to 15-degree longitude bands. Reality is political:

| Location | Longitude | `round(lon/15)` | Actual TZ | Error |
|----------|-----------|------------------|-----------|-------|
| Hawaii | -157.8 | **-11** | **-10** (HST) | **1 hour = 15 deg** |
| Western China | 80.0 | 5 | 8 (CST) | 3 hours = 45 deg |
| India | 82.5 | 6 | 5.5 (IST) | 0.5 hour = 7.5 deg |
| Nepal | 85.3 | 6 | 5.75 (NPT) | 0.25 hour |

The error propagates directly into the hour angle, which shifts the entire analemma curve in azimuth. For Hawaii, this meant the overlay was displaced by ~6.8 degrees.

After the fix, `TIMEZONE_OFFSET` is an optional field in `metadata.txt`. If provided, it overrides auto-detection. If not, auto-detection still runs but with a warning. `SkyMapper` and `ImageAnchorer` both accept the explicit timezone, and the metadata parser reads it and passes it through the pipeline.

#### Bugs fixed this prompt

Timezone handling (critical): `SkyMapper.__init__` used `round(longitude / 15)` which gives wrong results for locations where political timezones don't match geographic longitude bands. Added `TIMEZONE_OFFSET` support in metadata parser. Hawaii overlay shifted ~6.8 degrees in azimuth.

HP EoT fallback (critical): `calculator.py` line 161 had `eot_minutes = self.calculate_equation_of_time_approximate(day_of_year)` overwriting the Astropy-based EoT with the approximate formula. Implemented proper EoT calculation using Astropy's RA and mean solar longitude $L_0$. EoT = $(L_0/15 - \text{RA}_{\text{sun}}) \times 60$ minutes, following the NOAA convention.

Image projection missing cos(altitude) (critical): `sky_to_pixel()` used `delta_x = delta_az * pixels_per_degree_az` -- a flat linear mapping. 1 degree of azimuth subtends fewer pixels at higher altitudes because azimuth lines converge toward the zenith (like longitude lines converge at the poles). Applied `cos(mean_altitude)` correction. At the Hawaii anchor altitude of ~48 degrees, horizontal pixel offsets were ~33% too large.
