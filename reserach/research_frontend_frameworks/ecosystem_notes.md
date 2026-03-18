# Ecosystem Notes -- Specific Libraries Needed

The Analemma web frontend needs several specific capabilities regardless of which framework is chosen. This document covers the framework-agnostic and framework-specific options for each.

---

## HEIC Image Support

Mobile Safari (iPhone) shoots HEIC by default. Supporting HEIC upload requires client-side conversion since `<canvas>` and most browsers can't natively decode HEIC.

**Library: `heic2any`**
- npm: https://www.npmjs.com/package/heic2any
- Converts HEIC/HEIF to JPEG/PNG in the browser via WebAssembly
- ~200 kB additional bundle (significant, consider lazy-loading)
- Framework-agnostic -- works with any frontend
- Usage: `heic2any({ blob: heicBlob, toType: 'image/jpeg' })`

**Alternative: `libheif-js`**
- Lower-level, more control, similar bundle size
- Less convenient API

**Strategy:** Detect HEIC files by extension or MIME type, convert to JPEG on the client before sending to the Python backend. Lazy-load the conversion library (it's large).

---

## EXIF Parsing

The app needs to read EXIF data from uploaded images (GPS coordinates, timestamp, camera model, focal length) to pre-fill the metadata form.

**Library: `exifr`** (recommended)
- npm: https://www.npmjs.com/package/exifr
- ~50 kB gzip (with all parsers), or ~15 kB if you use selective imports
- Modern, fast, supports HEIC/HEIF, TIFF, JPEG, PNG
- Tree-shakeable -- only import what you need
- Framework-agnostic

**Alternative: `exif-js`**
- Older, simpler API, but less maintained and doesn't support HEIC
- Smaller bundle but missing features

**Fields to extract:**
- `GPSLatitude`, `GPSLongitude` -> pre-fill location
- `DateTimeOriginal` -> pre-fill timestamp
- `Make`, `Model` -> camera identification
- `FocalLength`, `FocalLengthIn35mmFilm` -> camera specs
- `ExifImageWidth`, `ExifImageHeight` -> image dimensions
- `Orientation` -> for proper display rotation

---

## Geocoding / Location Autocomplete

User types a city name, sees suggestions, selects one to populate lat/lon fields.

### Option A: Mapbox Geocoding API (recommended)
- Free tier: 100,000 requests/month
- `@mapbox/search-js-web` -- framework-agnostic web component for autocomplete
- Alternatively, their REST API is simple to call directly
- Returns lat/lon, place name, country

### Option B: Google Places Autocomplete
- Free tier: more limited, requires billing account
- `@googlemaps/js-api-loader` for loading the SDK
- React: `react-google-autocomplete`. Vue: `vue-google-autocomplete`. Svelte: use the API directly.
- Most feature-rich (includes photos, opening hours, etc.) but overkill

### Option C: Nominatim (OpenStreetMap)
- **Free, no API key required** (with usage policy: max 1 request/second, identify your app)
- REST API: `https://nominatim.openstreetmap.org/search?q={query}&format=json`
- No official JS SDK -- just fetch calls
- Returns lat/lon, display name
- Slightly less polished suggestions than Mapbox/Google
- Best option for a no-cost, no-account-needed solution

**Recommendation for this project:** Start with Nominatim (free, no API key). If autocomplete quality isn't good enough, switch to Mapbox free tier. Build the autocomplete dropdown yourself (it's a text input + debounced fetch + dropdown list -- 50-100 lines in any framework).

---

## Camera Sensor Database

The analemma overlay needs camera sensor dimensions to compute the field of view. The Python engine already handles this, but the web form could suggest sensor size based on camera model.

There's no good JS library for this. Options:
1. **Hard-code common sensors** -- build a small lookup table (50-100 common cameras) on the frontend
2. **Server-side lookup** -- let the Python backend handle it (it likely already has this data)
3. **Manual entry** -- just let the user enter sensor width/height or select from a dropdown

Recommendation: option 2 or 3. Don't over-invest in client-side camera database.

---

## Animation Libraries (for the analemma curve)

The animated figure-8 visualization is the showcase feature. The approach depends on the framework.

### SVG Path Animation (recommended approach)
The analemma curve can be represented as an SVG `<path>`. Animating it is a well-known technique:
1. Compute path data (from the Python backend or JS calculation)
2. Set `stroke-dasharray` to the path length
3. Animate `stroke-dashoffset` from path-length to 0

This creates the "drawing" effect -- the curve appears to be traced by an invisible pen.

**Framework-specific:**
- **Svelte:** Built-in `transition:draw` does exactly this. Simplest solution.
- **React:** `framer-motion` with `motion.path` and `pathLength` animated prop. Well-documented.
- **Vue:** CSS keyframes on `stroke-dashoffset`, or GSAP's `DrawSVGPlugin` (paid feature, but GSAP core is free and can animate the property manually).
- **Vanilla JS:** `requestAnimationFrame` loop or GSAP.

### Canvas Animation (alternative)
If the curve needs more visual effects (glow, particles, etc.), Canvas or WebGL is an option. But for a clean figure-8 curve drawing, SVG is simpler, more accessible, and resolution-independent.

### GSAP (GreenSock)
- Framework-agnostic, works everywhere
- ~25 kB gzip (core)
- The industry standard for web animation
- Free for most features; `DrawSVGPlugin` requires Club membership but isn't needed -- you can animate `stroke-dashoffset` with core GSAP

---

## Image Display and Download

**Displaying overlay images:**
The Python backend generates the overlay. The frontend fetches and displays it. All frameworks handle `<img>` tags identically. For zoom/pan on the overlay image, consider:
- `panzoom` (framework-agnostic, ~5 kB)
- `react-zoom-pan-pinch` (React-specific)

**Download:**
Create an `<a>` element with `download` attribute and a blob URL. This is framework-agnostic:
```js
const link = document.createElement('a');
link.href = URL.createObjectURL(blob);
link.download = 'analemma_overlay.png';
link.click();
```

---

## Local Storage / Cache

All frameworks can use `localStorage` directly. For a nicer API:
- **Vue:** `@vueuse/core` provides `useLocalStorage` composable
- **Svelte:** Svelte stores + `localStorage` wrapper (easy to write, or use `svelte-persisted-store`)
- **React:** `usehooks-ts` provides `useLocalStorage` hook

Cache the last-used metadata (coordinates, timezone, camera specs) so the user doesn't re-enter them. Cache the last uploaded image blob URL for quick re-display.

---

## CSS Framework

**Tailwind CSS** is the strong recommendation regardless of frontend framework:
- Works identically with React, Vue, Svelte, Astro
- Utility-first approach means responsive design is built into the class names (`md:`, `lg:` prefixes)
- No CSS-in-JS runtime cost
- Good for dark mode if desired
- Large community, excellent docs
- All the frameworks above have first-class Tailwind integration / setup guides
