# Image Format Compatibility

Research for the Analemma web app. Covers browser support, Pillow support, EXIF availability, and file size characteristics for every format users might upload.

## Format Matrix

| Format | Extensions | Browser `<input>` | Browser Preview | Pillow Read | EXIF | Typical Size (12MP) | Common Source |
|---|---|---|---|---|---|---|---|
| JPEG | .jpg, .jpeg | All | All | Native | Full | 3-8 MB | Everything |
| PNG | .png | All | All | Native | Limited | 15-30 MB | Screenshots, edited photos |
| HEIC | .heic | All* | Safari only | pillow-heif | Full | 2-5 MB | iPhone (default since iOS 11) |
| HEIF | .heif | All* | Safari only | pillow-heif | Full | 2-5 MB | Some Android, cameras |
| WebP | .webp | All | All modern | Native (Pillow >=9) | Limited | 2-6 MB | Android, Chrome screenshots |
| TIFF | .tiff, .tif | All | Chrome, Edge, Safari | Native | Full | 30-70 MB | Scanners, some cameras |
| CR2 | .cr2 | Varies | None | rawpy (not Pillow) | Via ExifTool | 20-30 MB | Canon RAW |
| NEF | .nef | Varies | None | rawpy (not Pillow) | Via ExifTool | 20-40 MB | Nikon RAW |
| ARW | .arw | Varies | None | rawpy (not Pillow) | Via ExifTool | 25-50 MB | Sony RAW |
| DNG | .dng | Varies | None | Pillow (limited) | Full | 20-60 MB | Adobe DNG, some phones |

*`<input type="file">` accepts any file type the OS file picker shows. HEIC files will appear in the picker on all platforms. But the browser can't render them for preview.

---

## Detailed Per-Format Analysis

### JPEG (.jpg, .jpeg)

The universal image format. Every camera, phone, and editing tool produces JPEG.

- **Browser support:** Universal. All browsers display JPEG natively. `<input type="file" accept="image/jpeg">` works everywhere.
- **Browser preview:** Universal. Can be displayed in `<img>`, drawn to `<canvas>`, processed with Web APIs.
- **Pillow:** Native support, no extra dependencies.
- **EXIF:** Full support. JPEG is the original home of EXIF data. All tags present.
- **File size:** Moderate. A 12 MP photo ranges from 3-8 MB depending on quality setting. Most phones default to ~4-5 MB.
- **Gotchas:** EXIF orientation tag is common -- photo may appear rotated if not handled. Already handled by the engine's `ImageOps.exif_transpose()`.

### PNG (.png)

Lossless format, common for screenshots and edited images.

- **Browser support:** Universal.
- **Browser preview:** Universal.
- **Pillow:** Native support.
- **EXIF:** Limited. PNG has its own metadata format (tEXt/iTXt chunks). Some tools embed EXIF in XMP within PNG, but it's not standard. Most PNGs from screenshots or editors have no EXIF at all.
- **File size:** Large. A 12 MP photo as PNG is 15-30 MB -- that's a painful upload on mobile. PNG is not a camera output format.
- **Use case:** Unlikely for sky photos. More likely for screenshots of someone else's photo (which will have no EXIF). Support it, but don't optimize for it.

### HEIC (.heic)

Apple's default photo format since iOS 11 (2017). Uses HEVC (H.265) compression inside an ISOBMFF container. 

- **Browser `<input>`:** The file picker will show HEIC files on all platforms. The OS doesn't gate file types by browser capability.
- **Browser preview:** Safari only (macOS and iOS, since Safari 11). Chrome, Firefox, Edge cannot display HEIC in `<img>` or `<canvas>`. Need heic2any for client-side conversion to JPEG for preview.
- **Pillow:** NOT native. Requires `pillow-heif` (v1.3.0, Feb 2026). After `register_heif_opener()`, `Image.open()` handles HEIC transparently. Binary wheels available for all platforms.
- **EXIF:** Full. iPhones embed complete EXIF including GPS, DateTimeOriginal, all camera data, and Apple-specific MakerNote.
- **File size:** Small. HEVC compression achieves ~50% smaller files than JPEG at equivalent quality. A 12 MP iPhone photo is typically 2-4 MB.
- **Critical for this project:** iPhones are the single most common smartphone camera. A large share of users will upload HEIC files. Failing to support HEIC would be a significant usability gap.

**iOS behavior note:** iOS has a "Most Compatible" setting that saves as JPEG instead of HEIC. But many users have the default "High Efficiency" (HEIC) setting. When sharing photos via AirDrop or email, iOS auto-converts to JPEG. But when uploading via a web form's `<input type="file">`, iOS sends the original HEIC.

### HEIF (.heif)

The container format that HEIC is based on. HEIF can use different codecs (HEVC for HEIC, AV1 for AVIF). In practice, .heif files are rare -- most HEIF files are HEIC files with the .heic extension.

Same support characteristics as HEIC. pillow-heif handles both.

### WebP (.webp)

Google's image format. Default for Android screenshots and some camera apps.

- **Browser support:** All modern browsers (Chrome 32+, Firefox 65+, Safari 16+, Edge 18+).
- **Browser preview:** Universal in modern browsers. Older Safari (pre-16) can't display WebP.
- **Pillow:** Native support since Pillow 9.0.
- **EXIF:** Partial. WebP can contain EXIF data, but many tools that produce WebP don't preserve it. Android camera apps that save WebP usually include EXIF. Screenshots and web-saved images usually don't.
- **File size:** Small; comparable to HEIC. A 12 MP photo is 2-6 MB.
- **Note:** WebP support in exifr (browser-side EXIF extraction) is not documented. Testing needed. For server-side, Pillow's `getexif()` works on WebP.

### TIFF (.tiff, .tif)

Professional and scientific image format. Supports lossless compression, 16-bit color, multiple layers.

- **Browser `<input>`:** Works.
- **Browser preview:** Partial. Chrome and Edge can display single-page TIFFs. Firefox has limited support. Safari handles most TIFFs.
- **Pillow:** Full native support.
- **EXIF:** Full. TIFF is the underlying format for EXIF data -- EXIF metadata is literally stored as an embedded TIFF structure.
- **File size:** Very large. A 12 MP TIFF can be 30-70 MB (uncompressed). Even LZW-compressed TIFFs are 15-30 MB.
- **Use case:** Unlikely for casual sky photos. Possible from professional photographers.

### RAW Formats (.cr2, .nef, .arw, .dng)

Camera-specific raw sensor data. Huge files with maximum dynamic range.

- **Browser support:** File picker will show them on some OSes (Windows shows DNG; macOS shows most RAW via Quick Look). Browsers cannot preview any RAW format.
- **Pillow:** Cannot open most RAW formats. DNG has limited Pillow support (reads the embedded JPEG thumbnail, not the raw data). Full RAW processing requires `rawpy` (Python bindings for LibRaw).
- **EXIF:** Present in the file but extractable only via ExifTool or rawpy. Pillow can't read it from RAW files.
- **File size:** 20-60 MB per image. Users uploading RAW are unusual for a web app.
- **Recommendation for V1:** Don't support RAW. It requires rawpy + LibRaw (complex native dependency), and the analemma engine doesn't benefit from raw sensor data -- it needs an RGB image for sun detection.

---

## V1 Format Support Recommendation

### Tier 1: Must Support (Day 1)

| Format | Why | What's Needed |
|---|---|---|
| **JPEG** | Universal. Most uploads will be JPEG. | Nothing -- Pillow handles it natively. |
| **HEIC** | iPhone default format. Large user base. | `pillow-heif` on server; `heic2any` on client for preview; `exifr` reads EXIF from HEIC directly. |
| **PNG** | Common for screenshots and edited images. | Nothing -- Pillow handles it natively. Won't have EXIF usually. |

### Tier 2: Should Support (V1 if Easy, V2 Otherwise)

| Format | Why | What's Needed |
|---|---|---|
| **WebP** | Increasingly common on Android. | Pillow 9+ handles it natively. Browser preview works. Test EXIF extraction. |
| **HEIF** | Rare as a distinct format from HEIC. | Covered by pillow-heif. |

### Tier 3: Nice to Have (V2+)

| Format | Why | What's Needed |
|---|---|---|
| **TIFF** | Uncommon for this use case. Huge files. | Pillow handles it natively. Consider a file size warning. |
| **DNG** | Some phones save DNG alongside JPEG. | Pillow has limited support. Might work for basic cases. |

### Tier 4: Out of Scope

| Format | Why Not |
|---|---|
| **CR2, NEF, ARW** (camera RAW) | Requires rawpy/LibRaw. Complex dependency. No benefit for sun detection. Vanishingly rare for web uploads. |

---

## Handling Unsupported Formats

The recommended approach for V1:

1. **Accept list in `<input>`:** Set `accept="image/jpeg,image/png,image/heic,image/heif,image/webp"` on the file input. This is a *hint* to the file picker, not a hard restriction -- users can still select "All Files".

2. **Client-side format detection:** Check the file extension and MIME type. For known-supported formats, proceed. For unknown formats, show a message: "This format isn't supported yet. Try saving the image as JPEG and uploading again."

3. **Server-side validation:** Attempt `Image.open()` (with pillow-heif registered). If it throws `UnidentifiedImageError`, return a 415 (Unsupported Media Type) response with a clear message.

4. **File size limit:** Set a reasonable upload limit. 25-30 MB covers the vast majority of phone photos (even TIFF under 12 MP). This naturally excludes most RAW files without needing explicit format rejection.

---

## Server-Side Changes for Format Support

The current engine uses `Image.open(image_path)` in `ImageAnchorer.__init__()`. To support HEIC:

```python
# At the top of image_anchor.py or in the server startup
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # HEIC support unavailable, JPEG/PNG still work
```

That's it. After registration, `Image.open()` handles HEIC transparently. The rest of the pipeline (sun detection, overlay rendering, EXIF transpose) works unchanged.

For the web server endpoint, the uploaded file comes as bytes in memory (not a file path). Use `BytesIO`:

```python
from io import BytesIO
image_bytes = await upload.read()  # from FastAPI UploadFile
im = Image.open(BytesIO(image_bytes))
```

This already works with all Pillow-supported formats including HEIC (with pillow-heif).

---

## Mobile vs Desktop Considerations

| Factor | Mobile | Desktop |
|---|---|---|
| Default format | HEIC (iPhone), JPEG/WebP (Android) | JPEG (most cameras) |
| GPS in EXIF | Usually present (if location services on) | Depends on camera (DSLRs often lack GPS) |
| Upload speed | Slower (cellular). HEIC's smaller size helps. | Fast (broadband). File size less critical. |
| EXIF orientation | Common (phones rotate freely) | Less common (DSLRs usually held level) |
| HEIC conversion for preview | Important (most mobile browsers are Chrome-based) | Important on Chrome/Firefox, not needed on Safari |
| Client-side processing speed | 2-4x slower than desktop for WASM (heic2any) | Fast |

For mobile users, the combination of exifr (fast EXIF read) + lazy-loaded heic2any (only when needed) is the right approach. Don't eagerly load the 200 kB WASM bundle; only fetch it when a HEIC file is actually selected.
