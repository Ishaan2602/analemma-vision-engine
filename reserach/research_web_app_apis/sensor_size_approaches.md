# Camera Sensor Size: Approaches and Feasibility

The analemma overlay engine needs `sensor_width_mm` and `sensor_height_mm` to compute the camera's angular field of view. Currently, users type these manually into metadata.txt. For the web app, we want to auto-detect or auto-fill these values from the uploaded photo.

## Background: Why Sensor Size Matters

The field of view (FOV) calculation is:

$$\text{FOV} = 2 \cdot \arctan\left(\frac{\text{sensor\_dimension}}{2 \cdot \text{focal\_length}}\right)$$

Without accurate sensor dimensions, the analemma curve gets placed at the wrong angular scale in the image. The focal length comes from EXIF (tag `FocalLength`), but sensor size is NOT a standard EXIF tag -- it's the missing piece.

## The Crop Factor Shortcut

Most cameras store two focal length values in EXIF:
- `FocalLength`: actual lens focal length (e.g., 4.25mm)
- `FocalLengthIn35mmFormat` (or `FocalLengthIn35mmFilm`): the 35mm-equivalent focal length (e.g., 26mm)

From these, you can derive the crop factor:

$$\text{crop\_factor} = \frac{\text{FocalLengthIn35mmFormat}}{\text{FocalLength}}$$

And from crop factor, you can derive sensor dimensions (assuming standard 3:2 aspect ratio sensor, since 35mm full frame is 36mm x 24mm):

$$\text{sensor\_width} = \frac{36}{\text{crop\_factor}}, \quad \text{sensor\_height} = \frac{24}{\text{crop\_factor}}$$

This works for most cameras. The catch: not all cameras write `FocalLengthIn35mmFormat`, and the 3:2 aspect ratio assumption breaks for some sensors (4:3, 16:9, 1:1).

## Approaches Evaluated

### 1. Static JSON Lookup Table (Manual Curation)

Hand-build a JSON file mapping camera Make+Model to sensor dimensions.

| Aspect | Assessment |
|---|---|
| Coverage | Only as good as what we manually add. Could start with 50-100 popular models. |
| Accuracy | Perfect -- we'd verify each entry. |
| Maintenance | Manual. New cameras require updates. |
| Implementation effort | Trivial. `camera_sensors.json` served from backend or bundled in frontend. |
| Data source | Various spec sheets, DPReview (archived), manufacturer sites. |

**Verdict**: Good as a curated fallback. Poor as a primary strategy because coverage is always incomplete.

### 2. Lensfun Database

[Lensfun](https://github.com/lensfun/lensfun) is an open-source library for correcting lens distortion. Its database contains camera models with a `cropfactor` field -- not raw sensor dimensions, but equivalent (see crop factor math above).

**Database format** (XML):
```xml
<camera>
    <maker>Pentax</maker>
    <model>Pentax K10D</model>
    <mount>Pentax KAF2</mount>
    <cropfactor>1.531</cropfactor>
</camera>
```

| Aspect | Assessment |
|---|---|
| Coverage | Good. Hundreds of cameras from major manufacturers. Community-maintained. |
| Accuracy | Good. Crop factors are verified by the community. |
| Maintenance | Community-maintained. Active project (122 contributors, 786 stars). |
| Implementation effort | Medium. Parse XML, convert cropfactor to sensor dims, match on Make+Model. |
| License | CC BY-SA 3.0 (database). LGPL-3.0 (code). |
| Data format | XML files, organized by manufacturer. |

**Verdict**: Strong option. We'd parse the lensfun XML at build time, extract Make+Model -> cropfactor mappings, convert to sensor dimensions, and serve as a JSON lookup. The CC BY-SA 3.0 license requires attribution but allows commercial use.

**Conversion**: `sensor_width = 36.0 / cropfactor`, `sensor_height = 24.0 / cropfactor`. For non-3:2 sensors we'd need to know the aspect ratio, but lensfun doesn't store that. Crop factor is defined relative to the diagonal of 35mm film (43.27mm), so more precisely: `diagonal = 43.27 / cropfactor`, then use aspect ratio to get width/height. For 3:2 sensors this simplifies to the formula above. For 4:3 sensors (most compacts/phones), width = diagonal * 4/5, height = diagonal * 3/5.

### 3. ExifTool Tag Derivation

[ExifTool](https://exiftool.org/) computes a "Composite" tag called `ScaleFactor35efl` from `FocalLength` and `FocalLengthIn35mmFormat`. It also derives `CircleOfConfusion` and `HyperfocalDistance` from this.

This isn't a database lookup -- it's the same crop factor math described above, but performed by ExifTool on the server side. ExifTool is a Perl program; we'd run it as a subprocess.

| Aspect | Assessment |
|---|---|
| Coverage | Any photo with both FocalLength and FocalLengthIn35mmFormat EXIF tags. |
| Accuracy | Depends on camera firmware writing correct values. Some phones are buggy. |
| Maintenance | None -- it's a computation, not a database. |
| Implementation effort | Low if ExifTool is already in the stack. Otherwise adds a Perl dependency. |

**Verdict**: Not worth adding ExifTool just for this. The same math can be done in Python or JavaScript in 3 lines. But this confirms that the crop-factor-from-EXIF approach is well-established.

### 4. Browser-Side EXIF Extraction (exifr)

[exifr](https://www.npmjs.com/package/exifr) is a JavaScript EXIF library that runs in the browser. MIT-licensed, zero dependencies, 794K weekly downloads, v7.1.3.

It reads `Make`, `Model`, `FocalLength`, `FocalLengthIn35mmFormat`, and all other standard EXIF tags from JPEG, HEIC, PNG, TIFF, and AVIF files. Performance is ~1ms per file in the browser using chunked reading (only reads the first few KB).

```javascript
import exifr from 'exifr'

// Extract only the tags we need
const tags = await exifr.parse(file, [
    'Make', 'Model', 'FocalLength', 'FocalLengthIn35mmFormat',
    'ImageWidth', 'ImageHeight'
])

// Derive crop factor
if (tags.FocalLength && tags.FocalLengthIn35mmFormat) {
    const cropFactor = tags.FocalLengthIn35mmFormat / tags.FocalLength
    const sensorWidth = 36.0 / cropFactor
    const sensorHeight = 24.0 / cropFactor
}
```

| Aspect | Assessment |
|---|---|
| Coverage | Any photo with the right EXIF tags. Very common in DSLR/mirrorless. Less reliable on phones. |
| Accuracy | Same caveats as approach #3. |
| Maintenance | None. |
| Implementation effort | Very low. npm install + 10 lines of code. |
| Runs in | Browser (no server round-trip needed). Also works in Node.js. |

**Verdict**: Excellent for V1. Extracts Make+Model for database lookup AND provides the focal length data for crop factor calculation, all client-side before the image even hits the server.

### 5. Online Camera Databases (digicamdb.com, camera-database.com)

Sites like digicamdb.com and camera-database.com have extensive camera spec listings including sensor dimensions.

| Aspect | Assessment |
|---|---|
| Coverage | Broad. Thousands of cameras. |
| API availability | **None.** These are scrape-only websites with bot protection. digicamdb.com uses proof-of-work challenges. |
| License | Unknown/proprietary. Scraping likely violates ToS. |
| Reliability | Websites can go down, change structure, add more bot protection. |

**Verdict**: Not viable. No API, can't legally scrape, and fragile even if we tried.

### 6. Crop Factor Computation from EXIF (Pure Math)

This is approach #3/#4 distilled: just do the math from EXIF tags. No external database, no API calls.

**When it works**: The camera wrote both `FocalLength` and `FocalLengthIn35mmFormat` into the EXIF. This covers most DSLRs, mirrorless cameras, and many smartphones (iPhone, Samsung Galaxy, Pixel).

**When it doesn't work**:
- Some older point-and-shoots don't write `FocalLengthIn35mmFormat`
- Some action cameras (GoPro) have unusual sensor geometries  
- Edited/re-saved images may have EXIF stripped
- Screenshots, renders, or non-photographic images have no relevant EXIF

**Aspect ratio caveat**: The 36/cropfactor x 24/cropfactor formula assumes 3:2 aspect ratio. Smartphones typically have 4:3 sensors. If we can detect the aspect ratio from `ImageWidth`/`ImageHeight` (also in EXIF), we can use the correct formula:

For a 4:3 sensor: `width = diagonal * 0.8`, `height = diagonal * 0.6` where `diagonal = 43.27 / cropfactor`.

| Aspect | Assessment |
|---|---|
| Coverage | ~70-80% of photos from real cameras. |
| Accuracy | Good when EXIF is present and correct. |
| Maintenance | None. |
| Implementation effort | Trivial. Pure math, no dependencies. |

**Verdict**: The most practical primary approach for V1. Combined with browser-side EXIF extraction (approach #4), this gives us sensor size for most uploads with zero API calls or database maintenance.

### 7. Crowdsourced / User-Contributed Database

Let users enter their camera's sensor size manually, and store it in our own database keyed by Make+Model. Over time, the database grows.

| Aspect | Assessment |
|---|---|
| Coverage | Starts empty. Grows with usage. |
| Accuracy | Depends on users entering correct values. Needs validation/moderation. |
| Maintenance | Automatic growth, but needs spam/error filtering. |
| Implementation effort | Needs a database, API endpoints, moderation logic. |

**Verdict**: Not appropriate for V1. Too much infrastructure for a hobby project launch. Could be a V2/V3 feature layered on top of the other approaches.

## Coverage Analysis

What percentage of real-world uploads would each approach handle?

| Scenario | EXIF crop factor (approach 6) | Lensfun DB (approach 2) | Static JSON (approach 1) |
|---|---|---|---|
| DSLR/mirrorless (Canon, Nikon, Sony, Fuji) | ~95% have both focal length tags | ~90% in lensfun DB | Depends on how many we add |
| Modern smartphone (iPhone 12+, Pixel, Galaxy S20+) | ~90% write FocalLengthIn35mmFormat | ~50% in lensfun (less phone coverage) | Easy to add top 20 phones |
| Older smartphone (pre-2018) | ~60% | ~30% | Low priority |
| Action camera (GoPro, DJI) | ~70% | ~40% | Easy to add |
| Point-and-shoot compact | ~50-70% | ~80% (lensfun's sweet spot) | Medium effort |
| Edited/re-saved (Photoshop, social media download) | ~10% (EXIF often stripped) | 0% (no Make/Model in EXIF) | 0% |

The EXIF crop factor approach covers the majority of real-world cases. Lensfun complements it well for cameras that don't write `FocalLengthIn35mmFormat` but are in the database. Static JSON is a targeted fallback for known gaps.

## Summary

The hybrid approach covers the most ground with the least effort:

1. **Primary**: Extract EXIF in browser (exifr), compute crop factor from focal lengths
2. **Fallback**: Look up Make+Model in a pre-built JSON derived from lensfun's database (cropfactor -> sensor dims)  
3. **Last resort**: Manual entry form where the user types sensor dimensions (with links to spec sheets)

This requires no external API calls, no server-side processing for sensor detection, and handles ~85-90% of real camera uploads automatically.
