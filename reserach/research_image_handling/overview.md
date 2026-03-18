# Image Handling & Animation Research -- Overview

Research conducted March 2026 for the Analemma web application. Three interconnected topics covering the image pipeline from upload to animated visualization.

## Research Files

- [exif_extraction.md](exif_extraction.md) -- EXIF extraction from uploaded images, including HEIC. JS and Python library comparison, recommended architecture.
- [image_format_compatibility.md](image_format_compatibility.md) -- Format-by-format analysis of browser support, Pillow support, EXIF availability, and file size. V1 format support recommendation.
- [analemma_animation.md](analemma_animation.md) -- Animated figure-8 visualization approaches. SVG vs Canvas vs CSS vs animation libraries. Backend API changes needed.

## Key Decisions Summary

### EXIF Extraction
- **Client-side:** Use `exifr` (npm, lite bundle, ~15 kB). Handles JPEG, HEIC, PNG, TIFF. Extracts GPS, datetime, camera data in ~3ms. Auto-fills the metadata form instantly.
- **Server-side:** Pillow's `getexif()` + `pillow-heif` for HEIC. Acts as a fallback if client-side extraction fails. No new Python dependency beyond `pillow-heif`.
- **Architecture:** Extract EXIF on client, send metadata alongside original image to server. Don't convert HEIC before upload -- the server handles it natively.

### Image Format Support (V1)
- **Must support:** JPEG, HEIC, PNG
- **Should support:** WebP, HEIF
- **Out of scope:** Camera RAW (.cr2, .nef, .arw)
- **New dependency:** `pillow-heif` (one pip install, one line of code to register)

### Analemma Animation
- **Approach:** SVG path overlay with Svelte's built-in `draw` transition
- **Backend change:** Add a `get_analemma_json()` method to `ImageAnchorer` that returns analemma points as JSON. Keep the static PNG overlay for downloads.
- **No animation library needed** -- Svelte handles it natively
- **Frontend structure:** Original photo as `<img>`, SVG positioned on top with `viewBox` matching image dimensions

## New Dependencies

| Where | Package | Size | Purpose |
|---|---|---|---|
| Python (requirements.txt) | `pillow-heif` | ~5 MB wheel | HEIC/HEIF support for Pillow |
| Frontend (npm) | `exifr` | ~15 kB gzip (lite) | Browser-side EXIF extraction |
| Frontend (npm) | `heic2any` | ~200 kB gzip | HEIC-to-JPEG conversion for browser preview (lazy-loaded) |

## Data Flow

```
[User selects photo]
    |
    +-- exifr reads EXIF from first 64 kB (~3ms)
    |     -> GPS, datetime, focal length, camera model
    |     -> Auto-fill form fields
    |
    +-- If HEIC and non-Safari browser:
    |     heic2any converts to JPEG for preview (~1-3s, lazy-loaded)
    |
[User reviews metadata, clicks Process]
    |
[Upload original file + metadata JSON to server]
    |
[FastAPI endpoint]
    +-- pillow-heif registered -> Image.open() handles any format
    +-- ImageAnchorer runs pipeline:
    |     detect sun -> calculate positions -> map to pixels
    |
    +-- Returns JSON:
          {
            original_image_url: "...",
            overlay_image_url: "...",     // static PNG for download
            analemma_data: { points, anchor, dimensions }
          }
    |
[Frontend receives response]
    +-- Displays original photo
    +-- Constructs SVG path from point data
    +-- User clicks "Show Analemma"
    +-- Svelte draw transition animates the curve
    +-- Dots and labels appear with staggered transitions
    +-- "Download" button fetches the static overlay PNG
```
