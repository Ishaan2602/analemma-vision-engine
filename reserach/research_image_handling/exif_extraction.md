# EXIF Extraction from Uploaded Images (Including HEIC)

Research for the Analemma web app. Goal: auto-fill the metadata form from EXIF data embedded in user-uploaded sky photos.

## Target EXIF Fields

These are the fields the analemma engine needs, mapped to their EXIF tag names:

| Metadata Field | EXIF Tag(s) | EXIF Tag ID | Notes |
|---|---|---|---|
| DATETIME | DateTimeOriginal | 0x9003 | In EXIF sub-IFD |
| LATITUDE | GPSLatitude + GPSLatitudeRef | 0x0002, 0x0001 | In GPS sub-IFD |
| LONGITUDE | GPSLongitude + GPSLongitudeRef | 0x0004, 0x0003 | In GPS sub-IFD |
| FOCAL_LENGTH_MM | FocalLength | 0x920A | In EXIF sub-IFD |
| CAMERA_MAKE | Make | 0x010F | In IFD0 |
| CAMERA_MODEL | Model | 0x0110 | In IFD0 |
| Crop factor hint | FocalLengthIn35mmFilm | 0xA405 | In EXIF sub-IFD |
| Orientation | Orientation | 0x0112 | In IFD0, for display rotation |

GPS coordinates in EXIF are stored as rational number arrays (degrees, minutes, seconds) with a separate reference tag (N/S, E/W). The library you pick needs to handle the conversion to decimal degrees.

---

## Browser-Side (JavaScript) Libraries

### 1. exifr (Recommended)

- **npm:** `exifr` -- v7.1.3 (latest)
- **Weekly downloads:** ~794,000
- **Bundle size:** Full ~50 kB gzip; lite ~15 kB gzip; mini ~5 kB gzip
- **Last published:** 5 years ago (but stable, no open critical issues)
- **TypeScript:** Built-in declarations

**HEIC support: YES.** Explicitly supports `.heic`, `.heif`, `.avif`, `.jpg`, `.tif`, `.png`. The lite bundle includes HEIC parsing. This is the big differentiator -- exifr can read EXIF from HEIC files *without converting the file first*.

**Key features for this project:**
- `exifr.gps(file)` returns `{latitude, longitude}` directly as decimal degrees. No manual DMS conversion needed.
- `exifr.parse(file, ['Make', 'Model', 'FocalLength', 'DateTimeOriginal'])` extracts only the tags you specify. Faster parsing, smaller memory footprint.
- Accepts `File`/`Blob` objects directly from `<input type="file">` -- perfect for upload forms.
- Chunked reading by default: only reads the first ~64 kB of the file in the browser. Important for large camera files (10+ MB) -- doesn't load the entire file into memory.
- Converts `DateTimeOriginal` to a JS `Date` object automatically (with `reviveValues: true`, which is the default).
- `orientation()` and `rotation()` methods for handling EXIF rotation.
- Isomorphic: works in browser and Node.js.
- Zero dependencies.

**Usage pattern for the analemma form:**
```js
import exifr from 'exifr/dist/lite.esm.mjs'

const file = inputElement.files[0]
const exif = await exifr.parse(file, {
  pick: ['DateTimeOriginal', 'GPSLatitude', 'GPSLongitude',
         'FocalLength', 'FocalLengthIn35mmFilm', 'Make', 'Model']
})
// exif.DateTimeOriginal -> Date object
// exif.latitude, exif.longitude -> decimal degrees (auto-converted)
// exif.FocalLength -> number (mm)
// exif.Make -> string
// exif.Model -> string
```

**Performance:** Benchmarked at ~2.5ms per file (vs 9.5ms for exifreader, 76ms for exiftool). On phones, expect 4-30ms. For a single file upload, this is imperceptible.

**Verdict: Use this.** It handles every format the project needs, including HEIC, directly in the browser. No conversion step required for EXIF extraction.

### 2. exif-js

- **npm:** `exif-js` -- v2.3.0
- **Weekly downloads:** ~106,000
- **Last published:** 9 years ago
- **TypeScript:** Community types (`@types/exif-js`)

**HEIC support: NO.** Only supports JPEG and TIFF per the EXIF v2.2 spec.

Older callback-based API (`EXIF.getData(img, callback)`). Requires the image to be fully loaded as an `<img>` element or read via FileReader. No chunked reading -- loads the entire file into memory. No tree-shaking. Global `EXIF` variable.

**Verdict: Skip.** Unmaintained, no HEIC, outdated API. exifr does everything exif-js does and more.

### 3. piexifjs

- **npm:** `piexifjs` -- v1.0.6
- **Weekly downloads:** ~89,000
- **Last published:** 6 years ago (npm page has no README)

piexifjs is primarily for *writing* EXIF data (inserting/modifying EXIF in JPEGs). It can read EXIF too, but it's JPEG-only. No HEIC, no PNG, no TIFF. The unique selling point is EXIF *modification* -- useful for post-processing but not for our read-only use case.

**Verdict: Skip.** Wrong tool for the job. We only need to read EXIF, and we need HEIC support.

### 4. Browser FileReader + Manual Parsing

You *could* read the file as an ArrayBuffer and parse EXIF manually. EXIF is a well-documented binary format (TIFF-based IFD structure). But:
- You'd be reimplementing what exifr already does
- HEIC container parsing is non-trivial (it's ISOBMFF-based, not JFIF)
- GPS rational-to-decimal conversion, endianness handling, tag dictionaries -- all boilerplate

**Verdict: No reason to do this.** exifr exists.

---

## Server-Side (Python) Libraries

### 1. Pillow (PIL) -- `Image.getexif()`

Pillow already handles EXIF for JPEG and TIFF. The `getexif()` method returns an `Exif` object (dict-like, keyed by numeric tag IDs). Access GPS data via `exif.get_ifd(ExifTags.IFD.GPSInfo)`.

**HEIC support:** Pillow does NOT natively open HEIC files. But with `pillow-heif` (see below), HEIC opens transparently and EXIF is accessible through the same `getexif()` API.

**Usage with pillow-heif:**
```python
from PIL import Image, ExifTags
from pillow_heif import register_heif_opener
register_heif_opener()

im = Image.open("photo.heic")
exif = im.getexif()
gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
# exif[ExifTags.Base.Make] -> 'Apple'
# exif_ifd[ExifTags.Base.DateTimeOriginal] -> '2024:03:15 14:30:00'
# gps[ExifTags.GPS.GPSLatitude] -> ((22, 1), (18, 1), (0, 1))
```

**GPS conversion needed:** Pillow returns GPS coords as tuples of rationals. You need to convert them to decimal degrees yourself:
```python
def gps_to_decimal(gps_coords, ref):
    d, m, s = [x[0]/x[1] for x in gps_coords]
    decimal = d + m/60 + s/3600
    if ref in ('S', 'W'):
        decimal = -decimal
    return decimal
```

**Verdict:** Fine for server-side EXIF if you're already opening the image with Pillow (which the engine does). The existing `ImageAnchorer` already calls `Image.open()` and `ImageOps.exif_transpose()`. Adding EXIF extraction there is minimal work.

### 2. PyExifTool (pyexiftool)

- **PyPI:** `PyExifTool` -- v0.5.6
- **License:** GPL-3.0 / BSD
- **Depends on:** Phil Harvey's `exiftool` CLI (must be installed separately, minimum v12.15)

This is a Python wrapper around the exiftool command-line tool. It runs exiftool in batch mode as a subprocess. ExifTool is the gold standard for metadata extraction -- it supports ~400 file formats, including every RAW format, HEIC, AVIF, and anything else a camera might produce.

**Pros:**
- Most comprehensive metadata extraction available anywhere
- Reads everything: EXIF, IPTC, XMP, MakerNotes, ICC profiles
- Handles HEIC, RAW (.cr2, .nef, .arw, .dng), and every other format
- Batch processing mode is efficient for multiple files

**Cons:**
- External dependency: requires `exiftool` (Perl) installed on the system. On Linux: `apt install libimage-exiftool-perl`. Adds complexity to Docker images.
- Subprocess communication overhead. Fine for single files but slower than in-process parsing.
- GPL license on the exiftool binary itself (though pyexiftool wrapper is BSD/GPL dual-licensed).

**Verdict:** Overkill for V1. If the only formats you're handling are JPEG and HEIC (99% of phone uploads), Pillow + pillow-heif covers it. ExifTool becomes valuable if you need to support RAW formats.

### 3. ExifRead (exifread)

- **PyPI:** `ExifRead` -- v3.5.1
- **License:** BSD-3-Clause
- **Pure Python, zero dependencies**
- **Supports:** TIFF, JPEG, JPEG XL, PNG, WebP, HEIC, RAW

This is a pleasant surprise. ExifRead is a pure-Python library that explicitly supports HEIC and most other formats we care about. No external dependencies, no C extensions. The `builtin_types=True` option returns standard Python types suitable for JSON serialization.

**Usage:**
```python
import exifread

with open("photo.heic", "rb") as f:
    tags = exifread.process_file(f, details=False, builtin_types=True)
# tags['EXIF DateTimeOriginal'] -> '2024:03:15 14:30:00'
# tags['GPS GPSLatitude'] -> [22, 18, 0]
# tags['Image Make'] -> 'Apple'
```

**Pros:** Lightweight, pure Python, supports HEIC natively, easy to add to requirements.txt.
**Cons:** Slightly less robust than Pillow's EXIF for edge cases. Tag keys are strings like `'EXIF DateTimeOriginal'` rather than numeric IDs.

**Verdict:** Good fallback option. But since the engine already uses Pillow, and pillow-heif gives us HEIC support there, ExifRead is a redundant dependency.

---

## HEIC-Specific Considerations

### Browser HEIC Support (as of March 2026)

**Can browsers natively display HEIC files?**

| Browser | HEIC/HEIF Image Display | Notes |
|---|---|---|
| Safari (macOS) | YES | Since macOS High Sierra / Safari 11 |
| Safari (iOS) | YES | Since iOS 11 |
| Chrome | NO | HEIC image display not supported; HEVC video partially supported on some hardware |
| Firefox | NO | No HEIC image support |
| Edge | NO | Same as Chrome (Chromium-based) |

**Summary:** Only Safari can natively display HEIC images. Chrome/Firefox/Edge cannot render HEIC in `<img>` tags or `<canvas>`. The `<input type="file">` element will *accept* HEIC files on all platforms (the OS file picker doesn't care about browser rendering), but the browser can't preview them.

**EXIF reading vs. image display are separate problems.** exifr can read EXIF from a HEIC Blob *without the browser being able to display the image*. So EXIF extraction works everywhere. But for previewing the uploaded image, you need conversion.

### HEIC Conversion Libraries

#### Client-Side: heic2any

- **npm:** `heic2any` -- v0.0.4
- **Weekly downloads:** ~464,000
- **Unpacked size:** 2.72 MB (the WASM decoder is large)
- **Last published:** 3 years ago

Converts HEIC to JPEG/PNG/GIF in the browser via WebAssembly. Browser-only (needs DOM and window).

**Known limitations:**
- Does NOT preserve EXIF metadata in the output. The converted JPEG/PNG has no EXIF. This means you must extract EXIF from the original HEIC blob *before* conversion (which exifr handles).
- Conversion is CPU-intensive. A 12 MP HEIC photo takes ~1-3 seconds on desktop, potentially longer on phones.
- 2.72 MB unpacked size. Should be lazy-loaded (only download the WASM when a HEIC file is detected).

**Usage:**
```js
import heic2any from 'heic2any'

const jpegBlob = await heic2any({
  blob: heicFile,
  toType: 'image/jpeg',
  quality: 0.85
})
// jpegBlob can be displayed in <img> and drawn to <canvas>
```

#### Client-Side: libheif-js

Lower-level alternative to heic2any. More control over decoding parameters but a less convenient API. Similar bundle size (WASM-based). Use heic2any unless you need fine-grained control.

#### Server-Side: pillow-heif

- **PyPI:** `pillow-heif` -- v1.3.0 (Feb 2026)
- **Supports:** Python 3.10 - 3.14, all major platforms (macOS, Windows, Linux, Alpine, Raspberry Pi)
- **Binary wheels available** for all platforms -- no manual libheif compilation needed

Registers as a Pillow plugin. After `register_heif_opener()`, `Image.open()` transparently handles HEIC/HEIF files. Supports reading EXIF, XMP, IPTC. Supports 8/10/12 bit HEIC.

**This is the right answer for server-side HEIC.** One line of code adds full HEIC support to the existing Pillow-based engine. Already has wheels for the Docker deployment target (Linux x86_64).

---

## Recommended Architecture

### The Decision: Client-Side EXIF + Server-Side Everything Else

**Extract EXIF on the client. Send metadata alongside the image. Process the image on the server.**

Here's the flow:

```
[User uploads image]
       |
[Browser: exifr reads EXIF from raw file]  -- ~3ms, works on HEIC
       |
[Auto-fill form fields: GPS, datetime, camera, focal length]
       |
[User reviews/edits metadata, clicks "Process"]
       |
[Browser: if HEIC, convert to JPEG via heic2any for preview]  -- lazy-loaded
       |
[Upload: send original image file + (possibly edited) metadata as JSON]
       |
[Server: Image.open() with pillow-heif registered]
[Server: engine processes image, returns overlay]
```

### Why This Architecture

1. **EXIF extraction is instant on the client.** exifr reads EXIF from the first 64 KB of the file in ~3ms. Users see their form auto-populated immediately after selecting a file. No waiting for upload + server round-trip.

2. **Users can correct the auto-filled data.** GPS might be missing (location services off), or the user might want to adjust the timestamp. Showing the extracted metadata in an editable form is better UX than having the server silently use whatever EXIF says.

3. **Send the original file to the server, not a converted copy.** Don't convert HEIC to JPEG on the client before upload. The server needs the original for sun detection (maximum dynamic range). The server handles HEIC natively via pillow-heif.

4. **The HEIC-to-JPEG conversion on the client is only for preview.** If the browser can't display HEIC, convert it on the client side just for the `<img>` preview. This conversion is lossy and metadata-destroying -- never use it for processing.

5. **Server-side EXIF extraction is a fallback**, not the primary path. If the client sends metadata from EXIF, the server uses it. If the client couldn't extract (old browser, JS disabled, edge case), the server can re-extract with Pillow + pillow-heif.

### What to Add to requirements.txt

```
pillow-heif>=1.3.0
```

That's it. One new dependency. ExifRead and PyExifTool aren't needed.

### What to Add to the Frontend

```
exifr        # ~15 kB gzipped (lite bundle) -- EXIF extraction
heic2any     # ~200 kB gzipped (WASM) -- lazy-loaded, only for preview
```

---

## Edge Cases and Gotchas

1. **GPS might be absent.** Many photos don't have GPS data (location services disabled, desktop screenshots, edited photos). The form must handle missing fields gracefully.

2. **DateTimeOriginal timezone ambiguity.** EXIF timestamps don't include timezone information. `2024:03:15 14:30:00` could be any timezone. The engine already handles timezone detection from GPS coordinates (via timezonefinder). The frontend should note that the timestamp is in the photo's local time.

3. **EXIF orientation.** Modern browsers auto-rotate images based on EXIF, but not consistently across all browsers. The engine's `ImageOps.exif_transpose()` already handles this server-side. On the client, exifr's `rotation()` method can help if you need to display the image correctly before upload.

4. **FocalLengthIn35mmFilm for sensor size.** If this tag is present alongside FocalLength, you can compute the crop factor: `crop_factor = FocalLengthIn35mm / FocalLength`. From there, sensor dimensions can be estimated (but only approximately -- the 35mm equiv is rounded). This is a nice-to-have for auto-filling sensor size.

5. **Stripped EXIF.** Social media apps strip EXIF from photos. If a user uploads a photo they previously shared on Instagram/WhatsApp, EXIF will be empty. The form must work without any EXIF at all.
