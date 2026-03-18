# Recommendations: V1 Implementation

## Geocoding: LocationIQ

**Pick LocationIQ for V1.** Here's why:

- **Most generous free tier**: 5,000 requests/day (~150K/month). For a hobby project, we'll never hit this.
- **No map display requirement**: Unlike Google and Mapbox, LocationIQ doesn't force you to show results on a proprietary map. We just want lat/long.
- **Autocomplete endpoint**: Dedicated `/v1/autocomplete` endpoint. Debounce at 300ms on the frontend and it works well.
- **Caching allowed**: We can cache results. If someone types "Hong Kong" we can store that result and not re-query.
- **Simple integration**: REST API, no SDK required. Or use their lightweight JS widget.
- **Worldwide OSM data**: Covers all our test locations (Sharjah, Nigeria, Russia, Hong Kong, Hawaii, Sweden, Canada, China).

**Second choice**: Geoapify. Similar profile -- generous free tier (3K credits/day), autocomplete endpoint, no map requirement, GDPR-compliant. Slightly less generous free tier but better documentation.

**Third choice**: MapTiler. Fastest claimed latency (<15ms). Great geocoding control component. But free tier is non-commercial only -- if the web app ever gets shared publicly, we'd need the $25/month Flex plan.

### Integration sketch (frontend)

```
User types in autocomplete box
  -> debounce 300ms
  -> GET https://api.locationiq.com/v1/autocomplete?key=KEY&q=INPUT&tag=place:city
  -> display dropdown of results (name + country)
  -> user clicks result
  -> extract lat, lon from response
  -> populate latitude/longitude fields in the form
```

API key goes in an environment variable, proxied through the backend to avoid exposing it in client-side code.

### Fallback plan

If LocationIQ ever becomes problematic (rate limits, downtime, ToS change), Geoapify and MapTiler are drop-in replacements -- same REST pattern, same response structure (GeoJSON-like). The frontend code changes are minimal: swap the base URL and API key.

---

## Camera Sensor Size: Hybrid EXIF + Lensfun

**Use a three-tier approach for V1:**

### Tier 1: Browser EXIF extraction + crop factor math

When the user uploads a photo, immediately parse EXIF in the browser using `exifr`:

```javascript
const tags = await exifr.parse(file, [
    'Make', 'Model', 'FocalLength', 'FocalLengthIn35mmFormat',
    'ImageWidth', 'ImageHeight'
])
```

If both `FocalLength` and `FocalLengthIn35mmFormat` are present, compute sensor dimensions directly:

```javascript
const cropFactor = tags.FocalLengthIn35mmFormat / tags.FocalLength
const sensorWidth = 36.0 / cropFactor   // for 3:2 sensors
const sensorHeight = 24.0 / cropFactor
```

Auto-populate the sensor fields. Also auto-populate Make, Model, and FocalLength since we need those too.

**Handles ~80% of uploads** from real cameras.

### Tier 2: Lensfun-derived JSON lookup

At build time, parse lensfun's XML camera database and generate a `camera_sensors.json` mapping `"Make Model"` -> `{ cropfactor, mount }`. Ship this as a static file (~50-100KB).

If Tier 1 fails (no `FocalLengthIn35mmFormat` in EXIF), but we have `Make` and `Model`, look up the camera in this JSON and compute sensor dimensions from the stored cropfactor.

**Handles another ~10-15%** -- mostly older cameras that lensfun has but that don't write the 35mm-equivalent focal length.

### Tier 3: Manual entry with guidance

If both Tier 1 and Tier 2 fail, show the sensor size input fields with:
- A helpful message: "We couldn't detect your camera's sensor size automatically."
- A link to a "how to find your sensor size" help page
- Pre-filled suggestions for common cameras (dropdown)
- The option to just use a "best guess" default (APS-C: 23.5 x 15.6mm) with a warning about reduced accuracy

### Implementation priority

| Step | What | Effort | Impact |
|---|---|---|---|
| 1 | Add exifr to frontend, extract EXIF on upload | ~2 hours | Covers ~80% of uploads |
| 2 | Parse lensfun XML into camera_sensors.json, add lookup | ~4 hours | Covers another ~10-15% |
| 3 | Manual entry form with defaults | ~1 hour | Covers remaining edge cases |

Total: about a day of work for ~95% automatic coverage.

### What about FocalLength?

We also need the actual focal length for the FOV calculation. This comes straight from EXIF (`FocalLength` tag) in Tier 1. If EXIF is stripped, the user enters it manually in Tier 3. The lensfun database doesn't help here -- it stores crop factors, not focal lengths.

### Aspect ratio handling

The 36/cropfactor x 24/cropfactor formula assumes 3:2 sensors (standard for DSLRs and mirrorless). Smartphones use 4:3, and some cameras use 16:9 or 1:1.

We can detect the sensor aspect ratio from `ImageWidth` / `ImageHeight` in EXIF (after accounting for EXIF orientation). Then:

```
diagonal = 43.27 / cropFactor
width = diagonal * cos(atan(height_ratio / width_ratio)) * (width_ratio / gcd)
height = diagonal * sin(atan(height_ratio / width_ratio)) * (height_ratio / gcd)
```

Or more simply, for common ratios:
- 3:2 -> width = 36/cf, height = 24/cf
- 4:3 -> width = 34.6/cf, height = 26.0/cf  
- 16:9 -> width = 39.9/cf, height = 22.4/cf

This is a refinement for after V1 works. For V1, the 3:2 assumption gets us within a few percent for most cameras, and the 4:3 case (smartphones) can be hardcoded as a special case.

---

## Decision Summary

| Feature | V1 Choice | Rationale |
|---|---|---|
| Geocoding | LocationIQ (free tier) | Most generous free tier, autocomplete, no map requirement, worldwide |
| Sensor size (primary) | exifr + crop factor math | Zero API calls, runs in browser, covers 80% of uploads |
| Sensor size (fallback) | Lensfun-derived JSON | Open data (CC BY-SA 3.0), good camera coverage, one-time build step |
| Sensor size (last resort) | Manual entry form | Always available, no dependencies |

### Open questions for implementation

1. **LocationIQ API key proxying**: Should the frontend call LocationIQ directly (simpler, exposes API key) or proxy through FastAPI (more secure, adds latency)? Recommendation: proxy through backend. The 300ms debounce already adds latency, so an extra 50ms for the proxy hop is negligible.

2. **Lensfun update cadence**: How often should we rebuild camera_sensors.json from the lensfun repo? Monthly? At deploy time? Recommendation: at deploy time, pull the latest lensfun XML from GitHub and rebuild. It's a build step, not a runtime dependency.

3. **Sensor aspect ratio**: How much effort does the 4:3 smartphone case deserve in V1? Recommendation: handle it. Phones are probably the most common upload source, and a 4:3 vs 3:2 error is noticeable (~4% FOV difference). A simple check on image aspect ratio is cheap.

4. **EXIF privacy**: Should we warn users that we're reading their photo's EXIF data? GPS coordinates, camera model, and datetime are in there. Recommendation: yes, a brief note in the upload UI. We don't store or transmit EXIF -- it's read client-side by exifr and discarded after extracting the fields we need.
