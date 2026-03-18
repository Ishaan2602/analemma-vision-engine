# Finalized Decisions

All 15 questions answered. These decisions are locked in for planning.

---

## 1. Frontend Framework -- **Svelte 5 / SvelteKit**

Built-in `draw` transition for the analemma animation. Smallest bundles. Lowest learning curve. SvelteKit with `adapter-static` for Vercel deployment.

## 2. Backend Framework -- **FastAPI**

Auto-generated Swagger UI, Pydantic validation, modern async foundation. Uvicorn workers. Containerized with Docker.

## 3. Deployment Configuration -- **Config 2: Vercel (frontend) + DigitalOcean App Platform (backend)**

- Frontend on Vercel free tier (auto-deploy, preview PRs, world-class CDN)
- Backend on DO App Platform, 1 vCPU / 2 GiB RAM ($25/mo covered by $200 student credit)
- ~8 months free, then migrate backend to Fly.io ($5-11/mo)
- Frontend stays on Vercel indefinitely

## 4. Domain Name -- **`.app` TLD from Name.com**

Free for 1 year via GitHub Student Developer Pack. The web app will live at the chosen `.app` domain. Backend at `api.<domain>.app`.

## 5. Geocoding API -- **LocationIQ**

5,000 req/day free tier. Autocomplete endpoint. No map display requirement. OSM-based, worldwide coverage. Cache results in localStorage.

## 6. Camera Sensor Size Detection -- **Three-tier automatic**

1. EXIF crop factor (FocalLength + FocalLengthIn35mmFormat) -- covers ~80% of uploads
2. Lensfun JSON lookup by Make+Model -- covers ~10-15% more
3. Manual entry fallback -- for the remainder

Lensfun XML parsed at build time into a static `camera_sensors.json`.

## 7. HEIC Handling -- **Both client and server**

- Client-side: exifr reads EXIF from HEIC natively (no conversion needed for metadata). heic2any converts to JPEG for browser preview only.
- Server-side: pillow-heif processes the original HEIC file for overlay rendering.
- The original file is uploaded to the server regardless of format.

## 8. Animation Approach -- **SVG path + Svelte `draw` transition**

The analemma figure-8 is rendered as an SVG `<path>` overlaid on the uploaded image. Svelte's built-in `transition:draw` animates the path being drawn. Individual sun positions are SVG `<circle>` elements with staggered fade-in. Interactive hover tooltips show date and altitude.

## 9. Backend Engine Changes -- **Both JSON + PNG endpoints**

- `POST /api/analyze` -- returns JSON with analemma point data (x, y, date, altitude, azimuth) for the frontend SVG animation. Fast (~1 second, computation only).
- `POST /api/render` -- returns a static PNG with the analemma overlay baked into the image. Used when the user clicks Download.

Two-phase response: the JSON endpoint fires first so the user sees the animated result almost instantly. The PNG renders on demand when they want a downloadable file.

## 10. Image Format Support -- **Day 1 Extended: JPEG, HEIC, PNG, WebP**

All four formats supported from launch. Pillow handles JPEG/PNG/WebP natively. pillow-heif adds HEIC. Frontend accept list: `.jpg,.jpeg,.heic,.heif,.png,.webp`.

## 11. Sample Images -- **All 6 CC-licensed images, personal photos excluded**

Gallery includes: brofjorden, cold_canada, hongkong, hunan, sharjah_sands, russia_meadow.

Excluded from repo and website: nigeria, raghav, raghav2, raghav6, robert_hawaii. Nigeria added to `.gitignore` alongside the existing raghav/robert exclusions.

## 12. Licensing -- **MIT code + CC per-image + NOTICE file**

- `LICENSE` at repo root: MIT, covering all source code
- `NOTICE` at repo root: third-party attribution for each CC image
- `input_images/README.md`: explains that images are not MIT-licensed
- Overlay outputs from CC BY-SA images labeled as CC BY-SA 4.0 on the website
- User uploads: not stored, not licensed by us

## 13. Frontend Layout -- **Concept B: Split Panel**

Desktop: image/result on the left (60%), controls on the right (40%). Mobile: collapses to single column. Dark theme (slate/navy background, gold/amber accent for the analemma curve). Inter font. Tailwind CSS.

## 14. EXIF Auto-Fill -- **Full auto-fill**

Auto-extract and pre-fill: datetime, GPS coordinates, focal length, camera make/model, and sensor size (via crop factor or lensfun lookup). User just verifies and clicks Generate.

## 15. Project Name -- **Analemma Vision**

The web app is called "Analemma Vision". Domain: `analemmavision.app` (or similar availability). Page title, README, and branding use this name.

---

## Additional Considerations -- Decisions

| Consideration | Decision |
|---|---|
| Process feedback / two-phase response | Yes. JSON endpoint returns fast (~1s). SVG animation plays. PNG rendered only on Download click. |
| Max upload size | 30 MB server-side limit. Client-side warning above 15 MB. |
| Ephemeris pre-download | Dockerfile `RUN` step pre-downloads JPL DE440 at build time. |
| Rate limiting | Basic IP-based rate limiting via slowapi. Not aggressive -- enough to prevent abuse. |
| Error messages | User-facing error messages translated from engine exceptions. "Sun not detected" instead of "ValueError". |
| Analytics | SimpleAnalytics (student pack, privacy-friendly, one script tag). |
| Caching | Geocoding results cached in localStorage. Sensor size lookups cached in localStorage. Image preview + EXIF kept in component state for re-generation without re-upload. |
| Accessibility | Not a V1 priority. |
| Optimistic UI | Yes -- show animated SVG result immediately from fast JSON endpoint while PNG renders in background only when requested. |
