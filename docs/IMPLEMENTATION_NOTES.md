# Analemma Project -- Implementation Notes

Technical details, theory explanations, and answers to implementation questions. Most recent at the top.

---

## Session 1

### Prompt 4 (2026-03-17)

### Why sigma capping matters for sun detection

The Gaussian blur sigma controls how much smoothing is applied when finding the brightness peak within a sun blob. For small blobs (radius ~11px like cold_canada), you want a tight sigma (~1.4) to accurately find the peak. For large blobs (radius 100-230px like hongkong/raghav), sigma=5 works well -- it smooths out noise without pulling the peak too far from the true center.

The adaptive formula `sigma = max(1, min(blob_radius * 0.12, cap))` was the solution. With cap=8, large blobs (hongkong: radius=228) got sigma=8, which over-smoothed and shifted the detection by 20+ pixels. With cap=5, those blobs get the same sigma=5 that was proven in Round 10, while cold_canada's small blob gets sigma=1.37 (well under the cap).

### Why cold_canada can't be improved further

cold_canada's sun blob at the 0.96 detection threshold contains 411 pixels with RGB values ranging only from 244 to 246 across all three channels. The entire blob is uniformly saturated to near-white. No weighting scheme (luminance, whiteness, centroid) can distinguish a meaningful center within this flat region. Different Gaussian sigma values shift the peak by a few pixels, but all are equally valid. The detection at (750, 235) is as good as any algorithm can achieve on this data.

### Coordinate parsing implementation

`parse_coordinate()` uses a two-pass approach:
1. Strip trailing direction letter (N/S/E/W) if present
2. Try parsing as a plain decimal (removing any trailing degree symbol)
3. If that fails, split on DMS separators (degree signs, prime marks, spaces, d/m/s letters) and convert degrees + minutes/60 + seconds/3600
4. Apply sign from direction letter (S and W → negative)

This covers everything from `40.1` to `8° 48' 26.98" E` without requiring users to standardize their format.

---

### Prompt 3 (2026-03-17)

#### Timezone rework: IANA database auto-detection

Replaced the `round(longitude/15)` timezone detection with a proper IANA database lookup using `timezonefinder` + Python's built-in `zoneinfo`. The new system:

- Detects IANA timezone name from (lat, lon) using `TimezoneFinder`
- Uses `ZoneInfo` to compute the exact UTC offset for the given reference datetime, correctly handling DST and half-hour offsets
- Three-tier fallback: explicit `timezone_offset` parameter > IANA auto > `round(lon/15)` with warning
- Added `reference_datetime` parameter to `SkyMapper.__init__()` for DST-aware detection
- Added `_iana_timezone_name` attribute to `SkyMapper` for diagnostics

Verified correct detection for 9 locations:
- Hawaii: -10 (was -11), Hong Kong: +8, Nigeria: +1, UIUC Sep: -5 (CDT), Oregon Jun: -7 (PDT), Houston Jan: -6 (CST), Sharjah: +4, W. China: +6, India: +5.5

#### scipy installed -- CV sun detection now functional

Root cause of all CV sun detection failures across images (hongkong, nigeria, raghav): `scipy` was not installed in the virtual environment. Without scipy, the `_detect_sun_position()` method fell back to simple brightest-pixel averaging, which fails with lens flare, reflections, and overexposed regions.

With scipy installed (v1.17.1), the pipeline now uses connected-component labeling (`ndimage.label`) to find the largest bright blob and computes its brightness-weighted center of mass.

#### Removed horizon cutoff from overlay

`generate_analemma_points()` in `image_anchor.py` previously filtered points with `altitude < 0`. This was removed -- all 365 points now have pixel coordinates computed. The image bounds are the only constraint on which points appear in the overlay. This correctly shows the analemma extending below the horizon (e.g., Sharjah sands, where the analemma dips to -16.6 deg altitude but the camera captures terrain below the horizon line).

#### Fixed spurious line in raghav6 overlay

The old `overlay_analemma()` drew a single continuous polyline through ALL in-bounds points. When a gap of out-of-bounds points separated two visible segments, the line jumped across the gap. Fixed by implementing segment-based line drawing: the line breaks whenever a point falls outside image bounds, preventing connections between non-adjacent visible points.

#### Other changes

- Default mode in `process_and_display()` changed from `'approximate'` to `'high-precision'`.
- Cell 11 (timezone diagnostic) rewritten to test IANA detection for 9 locations with fixed axes comparison.
- Created `docs/THEORY_AND_LIMITATIONS.md`.
- Added `scipy>=1.10.0` and `timezonefinder>=6.0.0` to requirements.txt.

#### Why does a near-zenith overlay appear "slim" while the sky chart appears "fat"?

At high altitude (~70 deg), `cos(70 deg) = 0.34`, meaning 1 degree of azimuth maps to only 0.34 degrees of apparent angular separation. The sky chart plots azimuth in true degrees (appearing wide), while the overlay correctly applies the cosine compression (appearing narrow). Physically correct behavior, not a bug. See `docs/THEORY_AND_LIMITATIONS.md` Section 5.1 for the full explanation.

#### Why was the Robert Hawaii small loop appearing too large in the overlay?

With the old timezone (UTC-11 instead of UTC-10), the anchor altitude was ~48 deg instead of ~34 deg. The `cos(altitude)` compression was stronger at 48 deg, making the loop appear differently sized compared to the sky chart. With correct timezone (UTC-10), the anchor altitude is ~34 deg and the overlay matches the sky chart proportions better.

---

### Prompt 2 (2026-03-16)

#### Why doesn't default timezone auto-detection handle DST?

The auto-detection formula `round(longitude/15)` produces the **standard time** offset for the longitude band. It has no concept of Daylight Saving Time because DST is a political/legal convention that varies by country, state, and even county.

For example, Oregon at longitude -122.6 auto-detects as UTC-8 (PST). But on June 1, Oregon observes PDT (UTC-7). If the photo's datetime field records the local clock time (13:45 PDT), using UTC-8 instead of UTC-7 introduces a 1-hour (15-degree azimuth) error.

Workaround: users in DST regions should set `TIMEZONE_OFFSET` in metadata to match the UTC offset of their clock at the time the photo was taken. For Oregon in summer: `TIMEZONE_OFFSET=-7`. (This was properly fixed in Prompt 3 with the IANA timezone system.)

#### What does the HP EoT sign convention mean?

The NOAA convention is: **EoT = apparent solar time - mean solar time**. Equivalently, EoT = (mean sun RA - true sun RA) in time units.

- **EoT > 0**: The true sun is *ahead* of the mean sun. Solar noon occurs *before* 12:00 clock time. The sun is further west than expected for the clock time.
- **EoT < 0**: The true sun is *behind* the mean sun. Solar noon occurs *after* 12:00 clock time.

In our implementation: `EoT_minutes = (L0/15 - RA_sun_hours) * 60`, where `L0` is the mean solar longitude. This is equivalent to the NOAA definition because `L0/15` gives the mean sun's RA in hours (modulo the small difference between ecliptic longitude and RA for the mean sun, which averages out over the year).

#### Why do we need TIMEZONE_OFFSET in metadata?

The recorded datetime in a photo's EXIF data (and therefore in our `metadata.txt`) is the **local clock time** at the moment of capture. The analemma calculation needs to convert this clock time into a **solar hour angle** -- the angular position of the sun relative to the observer's meridian. This conversion requires knowing the relationship between the local clock and UTC:

```
Hour Angle = (clock_time - 12:00) * 15 deg/hr + EoT/4 + (longitude - timezone_meridian)
```

The term `timezone_meridian = timezone_offset * 15` defines the "center longitude" that the local clock is synchronized to. The difference `longitude - timezone_meridian` corrects for the observer not being exactly on that meridian.

Auto-detection fails because the naive formula `round(longitude / 15)` assumes timezones are perfectly aligned to 15-degree longitude bands. Reality is political:

| Location | Longitude | `round(lon/15)` | Actual TZ | Error |
|----------|-----------|------------------|-----------|-------|
| Hawaii | -157.8 | **-11** | **-10** (HST) | **1 hour = 15 deg** |
| Western China | 80.0 | 5 | 8 (CST) | 3 hours = 45 deg |
| India | 82.5 | 6 | 5.5 (IST) | 0.5 hour = 7.5 deg |
| Nepal | 85.3 | 6 | 5.75 (NPT) | 0.25 hour |

The error propagates directly into the hour angle, which shifts the entire analemma curve in azimuth. For Hawaii, this meant the overlay was displaced by ~6.8 degrees.

After the fix, `TIMEZONE_OFFSET` is an optional field in `metadata.txt`. If provided, it overrides auto-detection. If not, auto-detection still runs but with a warning. `SkyMapper` and `ImageAnchorer` both accept the explicit timezone, and the metadata parser reads it and passes it through the pipeline.

#### Bugs fixed this prompt

Timezone handling (critical): `SkyMapper.__init__` used `round(longitude / 15)` which gives wrong results for locations where political timezones don't match geographic longitude bands. Added `TIMEZONE_OFFSET` support in metadata parser. Hawaii overlay shifted ~6.8 degrees in azimuth.

HP EoT fallback (critical): `calculator.py` line 161 had `eot_minutes = self.calculate_equation_of_time_approximate(day_of_year)` overwriting the Astropy-based EoT with the approximate formula. Implemented proper EoT calculation using Astropy's RA and mean solar longitude $L_0$. EoT = $(L_0/15 - \text{RA}_{\text{sun}}) \times 60$ minutes, following the NOAA convention.

Image projection missing cos(altitude) (critical): `sky_to_pixel()` used `delta_x = delta_az * pixels_per_degree_az` -- a flat linear mapping. 1 degree of azimuth subtends fewer pixels at higher altitudes because azimuth lines converge toward the zenith (like longitude lines converge at the poles). Applied `cos(mean_altitude)` correction. At the Hawaii anchor altitude of ~48 degrees, horizontal pixel offsets were ~33% too large.
