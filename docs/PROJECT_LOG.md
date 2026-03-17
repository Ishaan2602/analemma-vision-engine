# Analemma Project -- Session Log

Most recent work at the top.

---

## Session 1 -- started 2026-03-15

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
