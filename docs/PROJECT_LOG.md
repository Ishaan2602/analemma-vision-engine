# Analemma Project - Session Log

> **Rule**: Update this log at the start/end of every prompt session. Most recent work at the top.

---

## Session 4 -- 2025-03-17

### CV Sun Detection -- 13-Round Debug Cycle

The auto-detection algorithm (`_detect_sun_position()` in `image_anchor.py`) went through 13 rounds of iterative refinement across four problem images: cold_canada, russia_meadow, brofjorden, and hongkong. Full technical history is in `docs/CV_debugging.md`.

**Final algorithm** (Round 13):
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

### Metadata Parser -- Flexible Coordinate Formats

Added `parse_coordinate()` to `metadata_parser.py`. Handles:
- Plain decimal: `40.1`, `-88.2`
- Decimal with direction: `2.2945E`, `40.1N`, `40.1S`
- DMS with symbols: `8deg 48' 26.98" E`, `8 48 26.98 E`
- Unicode symbols: degree sign, prime, double-prime

All existing metadata files still parse identically.

### Cleanup

- Deleted `input_images/dummy/` entirely and removed its notebook cell
- Removed dummy from `docs/STRUCTURE.md`

### Diagnostic Results (all images, Round 13)

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

### Files Changed

- Modified: `analemma/image_anchor.py` (Round 13: progressive threshold + adaptive sigma capped at 5)
- Modified: `analemma/metadata_parser.py` (added `parse_coordinate()` for flexible coordinate formats)
- Modified: `docs/METADATA_REFERENCE.md` (documented flexible coordinate formats)
- Modified: `docs/STRUCTURE.md` (removed dummy references)
- Modified: `analysis.ipynb` (removed dummy cell)
- Created: `analemma/image_anchor_round12_baseline.py` (backup)
- Created: `docs/CV_debugging.md` (comprehensive 12-round debugging history)
- Deleted: `input_images/dummy/`

---

## Session 3 — 2026-03-17

### What we did

1. **IANA timezone auto-detection** — Replaced `round(longitude/15)` with `timezonefinder` + `zoneinfo` for proper timezone detection. Three-tier fallback: explicit > IANA auto > round(lon/15). Correctly handles DST (UIUC Sep = UTC-5 CDT), half-hour offsets (India = UTC+5.5), and political boundaries (Hawaii = UTC-10). Added `reference_datetime` parameter to `SkyMapper` for DST-aware detection.

2. **Installed scipy** — Root cause of ALL CV sun detection failures was scipy not being in the venv. With scipy 1.17.1, connected-component labeling + center-of-mass now works correctly for all test images.

3. **Removed horizon cutoff** — `generate_analemma_points()` no longer filters `altitude < 0`. All 365 points computed; only image bounds constrain visibility. Sharjah sands overlay now correctly shows analemma extending below horizon into sand dunes.

4. **Fixed spurious overlay lines** — Segment-based line drawing in `overlay_analemma()` breaks the polyline at out-of-bounds gaps, preventing lines connecting non-adjacent visible points (raghav6 fix).

5. **High-precision mode as default** — `process_and_display()` default changed from `'approximate'` to `'high-precision'`. All batch cells updated.

6. **Cell 11 timezone diagnostic rewrite** — Tests 9 locations with IANA detection table, fixed-axes comparison plots, and overlay plot showing the azimuth shift.

7. **Theory & Limitations report** — Created `docs/THEORY_AND_LIMITATIONS.md` covering: pinhole camera model, azimuth compression at high altitude, landscape orientation assumption, timezone handling, CV sun detection, FOV calibration, shape distortions, precision modes, and assumptions table.

8. **Documentation reorganization** — Moved `IMPLEMENTATION_NOTES.md` and `PROJECT_LOG.md` into `docs/`.

### Diagnostic Results (after all fixes)

| Dataset | TZ (IANA) | UTC Offset | Alt Range | Az Range | In Image / Total |
|---------|-----------|------------|-----------|----------|------------------|
| hongkong | Asia/Hong_Kong | +8.0 | 15.06-36.62 | 235.29-283.49 | 287/365 |
| robert_hawaii (HP) | Pacific/Honolulu | -10.0 | 15.41-34.69 | 75.39-124.32 | 125/365 |
| robert_hawaii (approx) | Pacific/Honolulu | -10.0 | 14.53-35.05 | 75.47-123.75 | 124/365 |
| nigeria | Africa/Lagos | +1.0 | 2.27-13.82 | 245.25-291.99 | 197/365 |
| raghav | America/Chicago | -5.0 (CDT) | -3.60-28.26 | 241.01-278.15 | 120/365 |
| raghav2 | America/Los_Angeles | -7.0 (PDT) | 20.86-67.20 | 186.06-201.96 | 149/365 |
| raghav6 | America/Chicago | -6.0 (CST) | 30.40-65.85 | 207.91-261.35 | 51/365 |
| sharjah_sands | Asia/Dubai | +4.0 | -16.56-5.59 | 250.72-293.49 | 257/365 |
| dummy | America/Chicago | -5.0 (CDT) | 25.39-69.97 | 141.44-170.07 | 180/365 |

### Key improvements vs Session 2

- Raghav2 (Oregon Jun): now correctly UTC-7 (PDT) instead of UTC-8 (PST) — 15 deg azimuth fix
- Raghav (UIUC Sep): now correctly UTC-5 (CDT) instead of UTC-6 (CST) — 15 deg azimuth fix
- Dummy (UIUC Jun): now correctly UTC-5 (CDT) instead of UTC-6 — same fix
- All "points below horizon" no longer filtered; "in image" count reflects actual image bounds
- No spurious lines in raghav6 overlay

### Files Changed

- Modified: `analemma/sky_mapper.py` (IANA timezone detection, reference_datetime, 3-tier fallback)
- Modified: `analemma/image_anchor.py` (reference_datetime passthrough, no horizon filter, segment-based lines)
- Modified: `analysis.ipynb` (all cells updated for HP default, timezone auto, cell 11 rewrite)
- Modified: `requirements.txt` (added scipy, timezonefinder)
- Created: `docs/THEORY_AND_LIMITATIONS.md`
- Moved: `IMPLEMENTATION_NOTES.md` -> `docs/IMPLEMENTATION_NOTES.md`
- Moved: `PROJECT_LOG.md` -> `docs/PROJECT_LOG.md`

---

## Session 2 — 2026-03-16

### What we did

1. **Fixed all 3 critical bugs** identified in Session 1:

   - **Bug #1 - Timezone auto-detection**: Added `timezone_offset` parameter to `SkyMapper.__init__()` and `ImageAnchorer.__init__()`. When auto-detecting via `round(lon/15)`, a `UserWarning` is now emitted. Added `TIMEZONE_OFFSET` field support to `metadata_parser.py` (float conversion). Added `TIMEZONE_OFFSET=-10` to `robert_hawaii/metadata.txt`.

   - **Bug #2 - HP EoT fallback to approximate**: Replaced the approximate fallback in `calculator.py` `calculate_high_precision()` with a proper Astropy-based EoT. Uses mean solar longitude $L_0 = (280.46646 + 0.9856474 \times n) \mod 360$ and Astropy's sun RA to compute $\text{EoT} = (L_0/15 - \text{RA}_\text{sun}) \times 60$ minutes. Initially had a sign error (`RA_sun - L0` instead of `L0 - RA_sun`); corrected to follow the NOAA convention. Mode comparison now shows max EoT diff = 5.3 min, max dec diff = 1.2 deg.

   - **Bug #3 - Linear image projection**: Added `cos(mean_altitude)` correction to `sky_to_pixel()` in `image_anchor.py`. Azimuth pixel displacement is now $\Delta x = \Delta\text{az} \times \cos(\bar{a}) \times \text{px/deg}$.

2. **Created project infrastructure files**:
   - `.github/copilot-instructions.md` — Custom instructions for auto-updating PROJECT_LOG.md and IMPLEMENTATION_NOTES.md after each prompt
   - `IMPLEMENTATION_NOTES.md` — Theory/implementation Q&A with session-dated entries

3. **Verified all fixes in notebook** — Restarted kernel, reran all cells:
   - Hong Kong: TZ=8 (auto, correct), alt 15.81-36.09, az 234.73-283.64, 365 visible
   - Robert Hawaii (approx): TZ=-10.0 (from metadata), alt 14.53-35.05, az 75.47-123.75
   - Robert Hawaii (HP): TZ=-10.0, alt 15.41-34.69, az 75.39-124.32 (genuinely different from approx now)
   - Mode comparison: max dec diff 1.2053 deg, max EoT diff 5.3455 min

4. **Added diagnostic cells for all remaining images** — Nigeria, Raghav (UIUC), Raghav2 (Oregon), Raghav6 (Houston), Sharjah Sands (UAE), Dummy (synthetic). Skipped raghav3/4/5 (identical metadata to raghav; raghav4 is .heic/unsupported). All 6 cells ran successfully.

5. **Completely rehashed TECHNICAL_DESCRIPTION.md** — Rewrote from scratch as a comprehensive ~350-line reference document covering: physical origin of the analemma, all mathematical formulas for both modes, full architecture description, CV pipeline details, metadata system, technologies, validation datasets, technical challenges and solutions.

### Diagnostic Results Summary

| Dataset | TZ (used) | Alt Range | Az Range | Visible/Total | Notes |
|---------|-----------|-----------|----------|---------------|-------|
| hongkong | 8 (auto) | 15.81-36.09 | 234.73-283.64 | 365/365 | Sunset, all visible |
| robert_hawaii (approx) | -10 (metadata) | 14.53-35.05 | 75.47-123.75 | 365/365 | Morning sun |
| robert_hawaii (HP) | -10 (metadata) | 15.41-34.69 | 75.39-124.32 | 365/365 | HP genuinely different |
| nigeria | 1 (auto) | 3.18-13.46 | 244.99-292.04 | 365/365 | Near-equatorial |
| raghav | -6 (auto) | -13.40-16.72 | 249.45-287.09 | 202/365 | Near-sunset, 163 below horizon |
| raghav2 | -8 (auto) | 18.11-60.88 | 200.50-230.38 | 365/365 | Oregon, high sun |
| raghav6 | -6 (auto) | 30.90-65.49 | 206.76-261.71 | 365/365 | Houston afternoon |
| sharjah_sands | 4 (auto) | -15.68-5.18 | 250.31-293.70 | 119/365 | Desert sunset, 246 below |
| dummy | -6 (auto) | 26.44-73.25 | 177.25-189.27 | 365/365 | Noon solstice synthetic |

### Known Limitation

Oregon (raghav2) auto-detected as UTC-8, but the photo datetime 2025-06-01 would be PDT (UTC-7). DST is not handled by the auto-detection. Users in DST regions should provide `TIMEZONE_OFFSET` in metadata reflecting the clock time offset at the time the photo was taken.

### Files Changed

- Modified: `analemma/calculator.py`, `analemma/sky_mapper.py`, `analemma/image_anchor.py`, `analemma/metadata_parser.py`
- Modified: `input_images/robert_hawaii/metadata.txt` (added TIMEZONE_OFFSET=-10)
- Modified: `analysis.ipynb` (added 7 new cells: 1 markdown + 6 diagnostic code cells)
- Modified: `docs/TECHNICAL_DESCRIPTION.md` (complete rewrite)
- Created: `.github/copilot-instructions.md`, `IMPLEMENTATION_NOTES.md`

---

## Session 1 — 2026-03-15

### What we did

1. **Comprehensive project review** — Read all docs (PROJECT_BRIEF, TECHNICAL_DESCRIPTION, USAGE_GUIDE, METADATA_REFERENCE, STRUCTURE, README) and all core source files (calculator.py, sky_mapper.py, plotter.py, image_anchor.py, metadata_parser.py, __init__.py).

2. **Subagent code audit** — Launched an automated thorough review of the entire codebase checking mathematical accuracy, relevance, code quality, and bugs. Findings summarized below.

3. **Organized docs** — Moved PROJECT_BRIEF.md, TECHNICAL_DESCRIPTION.md, USAGE_GUIDE.md, METADATA_REFERENCE.md, STRUCTURE.md into a `docs/` folder.

4. **Created analysis.ipynb** — Interactive notebook for running the pipeline on input images and visualizing results. Contains:
   - Import cell + helper function `process_and_display()` for any image
   - Hong Kong cell (approximate mode, overlay + sky chart + figure-8)
   - Robert Hawaii cells (approximate + high-precision mode)
   - Timezone diagnostic cell (auto -11 vs correct -10)
   - Mode comparison cell (approximate vs high-precision declination/EoT)

5. **Ran all notebook cells successfully** — All cells execute without errors. Results show the bugs clearly.

### Bugs Found (from audit + notebook diagnostics)

| # | Bug | Severity | Module | Confirmed |
|---|-----|----------|--------|-----------|
| 1 | **Timezone auto-detection wrong for Hawaii**: `round(-157.8/15) = -11`, actual is -10. Causes ~6.8 deg mean azimuth error (notebook confirms). | CRITICAL | sky_mapper.py | YES |
| 2 | **High-precision EoT falls back to approximate**: Line 161 of calculator.py explicitly uses `calculate_equation_of_time_approximate()` even in HP mode. Notebook confirms EoT diff = 0.000 between modes. | CRITICAL | calculator.py | YES |
| 3 | **Image projection is purely linear**: `sky_to_pixel()` uses `delta_az * pixels_per_degree_az` with no `cos(altitude)` correction. At alt=48 deg (Hawaii anchor), azimuth pixels are ~33% too wide. Causes tilt/shape mismatch between overlay and sky chart. | CRITICAL | image_anchor.py | Inferred |
| 4 | **No timezone field in metadata**: Parser doesn't support TIMEZONE_OFFSET. Users can't override bad auto-detection. | MODERATE | metadata_parser.py | YES |
| 5 | **Declination approximation ~1.2 deg max error** vs Astropy (around day 300, autumn). Acceptable for approximate mode. | MINOR | calculator.py | YES |

### Robert Hawaii Diagnosis

- **Overlay cut off**: Expected. FOV is narrow (28mm on 7.8mm sensor = ~15.8 deg horizontal). The analemma spans ~55 deg in azimuth, so most of it falls outside the frame. Not a bug.
- **Tilt mismatch**: Caused by bugs #1 (timezone) and #3 (linear projection). The sky chart shows the true alt/az shape, but the image overlay distorts it through the linear mapping and wrong timezone.
- **Approximate vs high-precision**: Nearly identical results because HP mode still uses approximate EoT (bug #2). Max declination diff is 1.2 deg but EoT diff is exactly 0.

### Planned Next Steps (discussed, not implemented)

- Fix timezone handling (add TIMEZONE_OFFSET to metadata, fix auto-detection or require explicit)
- Fix high-precision EoT (implement proper Astropy-based EoT)
- Fix image projection (add cos(altitude) correction to sky_to_pixel)
- Use notebook + reference images to verify analemma calculation accuracy
- (Optional) Build AI-powered metadata parser from natural language
- (Optional) Build web interface

### Files Changed

- Created: `analysis.ipynb`, `PROJECT_LOG.md`
- Moved to `docs/`: PROJECT_BRIEF.md, TECHNICAL_DESCRIPTION.md, USAGE_GUIDE.md, METADATA_REFERENCE.md, STRUCTURE.md
