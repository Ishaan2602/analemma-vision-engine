# Additional Considerations

Things that came up during research that are worth thinking about before or during implementation. These aren't blocking decisions -- they're design considerations, potential pitfalls, and ideas that don't fit neatly into the decision questions.

---

## Processing Time and User Experience

The engine takes several seconds to process an image (sun detection + 365 solar position calculations + overlay rendering). On a shared-CPU cloud instance, this could stretch to 10-15 seconds.

This creates a UX problem: the user clicks "Generate" and stares at a spinner for a while. Consider:

- **Progress feedback**: The backend could stream progress updates via Server-Sent Events (SSE) or WebSocket. "Detecting sun position... Calculating solar positions... Rendering overlay..." This turns a long wait into a process the user can watch.
- **Optimistic UI**: Show the animated SVG curve immediately from the JSON endpoint (which is fast -- just computation, no image rendering), then generate the downloadable PNG in the background.
- **Two-phase response**: First return the JSON data (fast, <1 second), then render the PNG on a separate endpoint when the user clicks Download. The animation plays while the download renders.

The two-phase approach aligns nicely with the SVG animation design. The user sees the result almost instantly (as an interactive SVG), and the heavyweight PNG rendering only happens when they actually want a file.

---

## Image Size Limits

Users could upload 20+ MB images (TIFF, high-res JPEG, RAW-converted). This affects:

- **Upload time**: On mobile cellular, a 20 MB upload could take 30+ seconds.
- **Server memory**: Pillow loads the entire image into memory as an uncompressed numpy array. A 48 MP photo at 8 bits/channel = ~140 MB of RAM just for the image data.
- **Processing time**: Sun detection scales with pixel count. A 48 MP image takes significantly longer than a 12 MP one.

Consider implementing:
- A client-side file size warning (> 15 MB: "This image is large and may take a while to process")
- Server-side max upload size (30 MB is reasonable)
- Optional client-side image resizing before upload (the analemma overlay doesn't benefit from ultra-high resolution -- 4000px wide is plenty for the curve accuracy)

---

## What Happens When the Ephemeris Isn't Pre-Downloaded

Astropy's high-precision mode downloads the JPL DE440 ephemeris (~17 MB) on first use. In a Docker container, this download should happen at build time. But if it doesn't:

- First request triggers a 17 MB download, adding 5-30 seconds to response time
- On Render/Heroku free tiers with ephemeral filesystems, the download happens on *every* cold start

The Dockerfile must include a step to pre-download the ephemeris:
```
RUN python -c "from astropy.coordinates import get_sun; from astropy.time import Time; get_sun(Time('2025-01-01'))"
```

This is a known pitfall with Astropy in containerized environments.

---

## Timezone Edge Cases

The engine auto-detects timezone from coordinates using TimezoneFinder + zoneinfo. This is robust for the 365-day year calculation. But there are edge cases:

- **Historical timezone changes**: If the photo is from a year when the timezone rules were different (e.g., a country changed its UTC offset), the calculation could be slightly off. TimezoneFinder uses current boundaries.
- **Locations near timezone boundaries**: GPS coordinates a few hundred meters from a timezone boundary might resolve to the wrong zone. The engine already handles this gracefully (the error is tiny -- one timezone hour shift changes azimuth by ~15 degrees, which is noticeable but not catastrophic).
- **Users who lie about their location**: If someone enters coordinates in one timezone but a datetime that only makes sense in another, the result will be wrong. Not much we can do about this -- it's user error.

No action needed here -- just something to be aware of.

---

## Offline / PWA Potential

The frontend is a static SPA. With a service worker, it could work partially offline:
- The form and UI load from cache
- Sample images could be pre-cached
- Only the actual analemma computation requires the backend

This is a "nice to have" for V2. SvelteKit supports service workers natively. The main benefit: users in low-connectivity areas (which is where some of the coolest sky photos come from) could at least load the app and prepare their upload.

---

## Rate Limiting

Without accounts, there's no per-user tracking. But the backend should have basic rate limiting to prevent abuse:
- IP-based rate limit: 10-20 requests per minute per IP
- Global rate limit: prevent a single server from being overwhelmed
- File size limit: 30 MB max upload

FastAPI doesn't have built-in rate limiting, but `slowapi` (a ASGI rate limiter built on `limits`) works well. Or use the deployment platform's rate limiting (DigitalOcean App Platform has configurable rate limits).

---

## The "What About Pyodide?" Question

Pyodide lets you run Python in the browser via WebAssembly. In theory, you could run the entire analemma engine client-side, eliminating the backend entirely.

**Why this probably doesn't work for V1:**
- Astropy is huge (~50 MB compiled) and loading it via Pyodide takes 15-30 seconds on first load
- scipy's native extensions have partial Pyodide support but it's fragile
- Pillow in Pyodide has limited format support
- The user experience of a 30-second initial load is unacceptable

**Worth revisiting later**: If Pyodide's ecosystem matures and astropy gets a lightweight mode, a fully client-side version would be interesting. It would eliminate hosting costs entirely.

---

## Testing Strategy

The engine has existing tests (`tests/test_calculator.py`). For the web app, consider:

**Backend tests:**
- Unit tests for the API endpoint (FastAPI's `TestClient`)
- Integration test: upload a sample image, verify the response is a valid PNG
- Test HEIC handling with a sample HEIC file
- Test error cases: missing fields, corrupt image, unsupported format

**Frontend tests:**
- Component tests with Svelte's testing utilities (vitest + @testing-library/svelte)
- Test EXIF extraction with sample files
- Test the sensor size lookup logic
- E2E tests with Playwright (upload image, fill form, verify result appears)

**CI:**
- GitHub Actions runs tests on PR
- Frontend: `npm run test` + `npm run build` (catch build errors)
- Backend: `pytest` (existing engine tests + new API tests)

---

## Error Messages That Actually Help

When things go wrong, the error message should tell the user what to do, not what the server threw. Examples:

- "Sun not detected in the image -- try a photo where the sun is clearly visible" (instead of "ValueError: no blob found above threshold")
- "The image appears to be too dark for sun detection" (if the max brightness is below a threshold)
- "Invalid GPS coordinates -- please check latitude and longitude" (instead of a 422 validation error dump)
- "Processing took too long -- try a smaller image" (timeout)

The engine's error messages are developer-focused. The API layer should translate them into user-facing language.

---

## Analytics

You mentioned Simple Analytics is in the student pack (privacy-friendly, free for a year with 100K page views/month). It's worth adding to understand:
- How many people actually use the tool
- Which sample images are most popular
- Where users drop off (do they upload but not fill in all fields?)
- Mobile vs desktop split

Simple Analytics has no cookies, no tracking pixels, and complies with GDPR without a cookie banner. One script tag in the HTML head.

---

## Caching and Performance

The user mentioned local storage and cache. Specific opportunities:

- **Geocoding cache**: Store recent location lookups in localStorage. If the user types "Hong Kong" twice, don't hit the API again.
- **Sensor size cache**: Once a camera model's sensor size is resolved, cache it in localStorage.
- **Image preview**: Keep the uploaded image's object URL and EXIF data in component state so the user can re-generate without re-uploading.
- **API response caching**: The backend could cache computation results keyed by (lat, lon, datetime, camera params). Same inputs always produce the same output. But this requires a cache store (Redis, or even just an in-memory dict with LRU eviction). Probably overkill for V1.

---

## Accessibility Compliance

The site should be WCAG 2.1 AA compliant at minimum. Key areas:

- The SVG overlay needs proper ARIA labels for screen readers
- Color contrast ratios for text on dark backgrounds (Tailwind's slate palette is designed for this)
- The animation should respect `prefers-reduced-motion`
- Form error messages should be announced to screen readers via `aria-live`
- The file input should work with keyboard navigation
- Alt text for the sample images

Svelte and Tailwind both have good accessibility tooling. `@sveltejs/kit` includes an accessibility checker that runs during development.

---

## What Happens After the Student Credits Run Out

This is worth thinking about now even though it's months away:

- **Frontend**: Stays on Vercel for free, indefinitely. No action needed.
- **Backend**: Needs a paid host or migration. Fly.io at $5-11/month is most cost-effective. If you don't want to pay anything, shut down the backend and add a banner: "Backend is offline -- contact me to request processing."
- **Domain**: Renew at retail price (~$15-20/year) or switch to the free `yourproject.vercel.app` subdomain.
- **If the project gets traction**: Look into sponsorship, donations, or university funding to cover hosting.

---

## Mobile Camera Integration

Currently, `<input type="file" accept="image/*">` on mobile shows the camera roll. But you could also offer:
- **Take a photo**: `<input type="file" accept="image/*" capture="environment">` opens the camera directly. For a sun photo, this is convenient. But the quality depends on the phone's default camera app behavior.
- **Multiple photos**: Not needed for V1 (one image per analemma), but could be useful for batch processing later.

The `capture` attribute behavior varies across mobile browsers. On iOS Safari, it opens the camera; on Android Chrome, it might offer a choice between camera and gallery. Test this on target devices.

---

## Open Source Visibility

If you want the project to get attention:
- Add relevant GitHub topics: `astronomy`, `sun`, `analemma`, `computer-vision`, `image-processing`, `python`, `svelte`, `fastapi`
- Write a compelling README with a demo GIF showing the animation
- Submit to "awesome" lists (awesome-python, awesome-svelte, awesome-astronomy)
- Post on relevant subreddits (r/astronomy, r/astrophotography, r/sveltejs, r/Python)
- The animated visualization is inherently shareable -- consider a "share to Twitter/X" button

---

## Internationalization (i18n)

Not needed for V1, but the app has natural international appeal (the analemma is visible from everywhere on Earth). If you ever want to add i18n:
- SvelteKit has `svelte-i18n` and `typesafe-i18n` libraries
- The main strings to translate: form labels, error messages, button text, help text
- Coordinate formats vary by locale (comma vs period for decimals)
- Date/time formats vary by locale

Not a V1 concern, but worth noting because the architecture choice (SvelteKit or not) affects how easy it is to add later.
