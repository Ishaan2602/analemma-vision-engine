# Analemma Engine - Technical Description

**Python computational system for solar position calculation, astronomical visualization, and automated computer vision-based image overlay of the solar analemma.**

**Language**: Python 3.8+ | **Architecture**: 4-layer modular design | **Precision modes**: Approximate (Spencer 1971) and High-Precision (Astropy/JPL DE440)

---

## 1. The Analemma: Physical Origin

The analemma is the figure-8 traced by the sun's position in the sky when observed from the same location, at the same clock time, across an entire year. Its shape is governed by two independent astronomical phenomena:

### 1.1 Solar Declination (vertical axis)

Earth's rotational axis is tilted 23.45 degrees relative to its orbital plane (the obliquity of the ecliptic). As Earth orbits the sun, the sub-solar latitude oscillates between +23.45 degrees (summer solstice, ~June 21) and -23.45 degrees (winter solstice, ~Dec 21), passing through 0 degrees at the equinoxes.

From any fixed observer, this manifests as the sun being higher in summer and lower in winter at the same clock time - the vertical extent of the analemma.

### 1.2 Equation of Time (horizontal axis)

The sun does not cross the local meridian at exactly 12:00 noon every day. The deviation, called the Equation of Time (EoT), arises from two effects:

1. **Orbital eccentricity** (e = 0.0167): Earth moves faster at perihelion (January) and slower at aphelion (July) per Kepler's second law. This creates a sinusoidal component with a period of one year.

2. **Obliquity of the ecliptic**: The sun's apparent motion along the ecliptic projects onto the celestial equator non-uniformly. Near the solstices, the ecliptic longitude changes mostly in the RA direction; near the equinoxes, a portion of the motion goes into declination. This creates a sinusoidal component with a period of half a year.

Combined, these two effects produce the asymmetric figure-8 shape where the larger lobe is in the southern (winter) hemisphere and the crossing point falls in mid-April and early September.

---

## 2. Mathematical Foundations

### 2.1 Approximate Mode (Spencer 1971)

**Solar Declination:**

$$\delta \approx 23.45° \times \sin\left[\frac{360°}{365}(284 + N)\right]$$

where $N$ is the day of year (1-365). The phase offset of 284 days shifts the sine wave so that $\delta = 0$ at the vernal equinox ($N \approx 81$) and $\delta = +23.45°$ at the summer solstice ($N \approx 172$).

**Equation of Time (Spencer approximation):**

$$B = \frac{2\pi(N - 81)}{365}$$

$$\text{EoT} = 9.87\sin(2B) - 7.53\cos(B) - 1.5\sin(B) \quad \text{[minutes]}$$

The $9.87\sin(2B)$ term is the obliquity component (half-year period), while $-7.53\cos(B) - 1.5\sin(B)$ is the eccentricity component (full-year period). Extrema: approximately +14.3 min (early February) and -16.4 min (early November).

### 2.2 High-Precision Mode (Astropy/JPL Ephemeris)

**Solar Declination:** Obtained directly from Astropy's `get_sun()` function, which queries the JPL DE440 or DE441 development ephemeris. This accounts for nutation, aberration, and the true orbital elements rather than the mean values used in approximations.

**Equation of Time:** Computed from the difference between the mean sun's right ascension and the true sun's right ascension:

$$L_0 = (280.46646 + 0.9856474 \times n) \mod 360° \quad \text{[mean solar longitude]}$$

where $n$ is the number of days since J2000.0 (JD 2451545.0).

$$\text{RA}_{\text{mean}} = L_0 / 15 \quad \text{[hours]}$$

$$\text{EoT} = (\text{RA}_{\text{mean}} - \text{RA}_{\text{sun}}) \times 60 \quad \text{[minutes]}$$

with the result normalized to the range $[-720, +720]$ minutes (i.e., $\pm 12$ hours) to handle the RA wraparound at 0h/24h. This follows the NOAA sign convention: positive EoT means the true sun is ahead of the mean sun (sun crosses meridian before noon).

The HP mode produces declination differences of up to ~1.2 degrees and EoT differences of up to ~5.3 minutes compared to the approximate mode. These are real physical differences, not errors - the approximate formulas are simplified models.

### 2.3 Horizon Coordinates

**Hour Angle:** The angular distance of the sun from the observer's meridian, measured westward:

$$H = (t_{\text{obs}} - 12) \times 15°/\text{h} + \text{EoT} / 4 + (\lambda - \lambda_{\text{tz}})$$

where:
- $t_{\text{obs}}$ is the observation time in decimal hours (local clock time)
- The factor of 15 deg/h converts time to angular measure (360 deg / 24 h)
- $\text{EoT}/4$ converts EoT from minutes to degrees (15 deg/h / 60 min/h = 0.25 deg/min)
- $\lambda$ is the observer's longitude
- $\lambda_{\text{tz}} = \text{timezone\_offset} \times 15°$ is the longitude of the timezone's central meridian

**Solar Altitude** (spherical law of cosines for the astronomical triangle):

$$\sin(a) = \sin(\phi)\sin(\delta) + \cos(\phi)\cos(\delta)\cos(H)$$

where $\phi$ is the observer's latitude.

**Solar Azimuth** (from spherical trigonometry):

$$\sin(A) = \frac{\cos(\delta)\sin(H)}{\cos(a)}$$

$$\cos(A) = \frac{\cos(\delta)\cos(H)\sin(\phi) - \sin(\delta)\cos(\phi)}{\cos(a)}$$

Both components are used via $\text{atan2}(\sin A, \cos A)$ for correct quadrant determination. The result is normalized to $[0°, 360°)$ measured clockwise from North.

### 2.4 Derived Quantities

**Maximum altitude** (sun on the meridian, $H = 0$):

$$a_{\max} = 90° - |\phi - \delta|$$

**Sunrise/Sunset hour angle** (altitude = 0):

$$\cos(H_0) = -\tan(\phi)\tan(\delta)$$

Returns `None` for polar day ($|\delta| > 90° - |\phi|$) or polar night.

**Solar noon** (true noon, when sun crosses meridian):

$$t_{\text{noon}} = 12\text{h} - \text{EoT}/60 - (\lambda - \lambda_{\text{tz}})/15$$

---

## 3. Architecture

The system follows a strict 4-layer architecture where each layer has a single responsibility and communicates only through well-defined data structures (Python dicts and lists).

### Layer 1 - Physics Engine: `AnalemmaCalculator` (`calculator.py`)

**Responsibility:** Pure numerical computation of solar declination and equation of time for a given date.

- **Input:** A date (or year + time-of-day for bulk calculations)
- **Output:** `{declination, eot, day_of_year, date}` dict per day
- **Mode switching:** Constructor parameter `mode='approximate'` or `mode='high-precision'`
- **Key method:** `calculate_year(hour, minute, days=365)` generates 365 data points for the entire year at the specified clock time
- **Comparison:** `compare_modes(date)` returns both modes' results and their differences

Constants:
- `OBLIQUITY = 23.45` degrees
- `DAYS_PER_YEAR = 365.25`
- `VERNAL_EQUINOX_OFFSET = 81` days

### Layer 2 - Coordinate Mapper: `SkyMapper` (`sky_mapper.py`)

**Responsibility:** Transform celestial coordinates (declination, EoT) to local horizon coordinates (altitude, azimuth) for a specific observer location.

- **Input:** Calculator output + observer latitude/longitude/timezone
- **Output:** Enhanced dicts with added `{altitude, azimuth, hour_angle}` fields
- **Timezone handling:** Three-tier system: explicit `timezone_offset` parameter > IANA auto-detection via `timezonefinder`/`zoneinfo` (DST-aware) > `round(longitude/15)` fallback with warning
- **Key method:** `map_to_horizon(calc_results)` transforms an entire year of calculator data

The IANA detection was necessary because `round(longitude/15)` fails for:
- Hawaii: longitude -157.8 gives `round(-157.8/15) = -11`, actual is UTC-10
- China: uses UTC+8 despite spanning longitudes 73-135
- India: UTC+5:30, a half-hour offset that `round()` can't produce

### Layer 3 - Visualization: `AnalemmaPlotter` (`plotter.py`)

**Responsibility:** Generate publication-quality plots from calculator and mapper output.

Six plot types are available:

| Method | Data Source | Description |
|--------|-----------|-------------|
| `plot_analemma()` | sky_data | Altitude vs. Azimuth scatter with day-of-year coloring and compass labels |
| `plot_figure8()` | calc_data | EoT vs. Declination (the "pure" analemma, location-independent) |
| `plot_time_series()` | calc_data | Declination and EoT as line plots over the year (2-subplot figure) |
| `plot_sky_dome()` | sky_data | Polar projection with azimuth as angle and altitude as radius |
| `plot_interactive()` | sky_data | Plotly interactive scatter with hover tooltips (date, alt, az) |
| `plot_comparison()` | approx + HP data | 2x2 grid comparing declination and EoT between modes |

All static plots use matplotlib (300 DPI export), with optional SVG/PDF vector output. The interactive plot requires Plotly (checked via `PLOTLY_AVAILABLE` flag).

### Layer 4 - Computer Vision: `ImageAnchorer` (`image_anchor.py`)

**Responsibility:** Overlay a computed analemma onto a real photograph, anchored to the sun's detected position.

This layer composes all three other layers internally:
- Creates its own `AnalemmaCalculator` (with configurable `mode`)
- Creates its own `SkyMapper` (with configurable `timezone_offset`)
- Uses `AnalemmaPlotter` for composite visualizations

**Key parameters:**
- `image_path`: Path to the photograph
- `anchor_datetime`: When the photo was taken (determines which point on the analemma is anchored to the detected sun)
- `latitude`, `longitude`: Observer's GPS coordinates
- `timezone_offset`: Explicit UTC offset (or `None` for auto-detection)
- `mode`: Calculation precision mode
- `auto_detect_sun`: Whether to run the CV sun detection pipeline

---

## 4. Computer Vision Pipeline

### 4.1 Sun Detection (`_detect_sun_position()`)

The detection pipeline uses progressive thresholding with adaptive Gaussian refinement:

1. **EXIF correction:** `PIL.ImageOps.exif_transpose()` handles camera orientation tags before any pixel processing
2. **Grayscale conversion:** Takes `max(R, G, B)` per pixel (not luminance-weighted average), since the sun saturates all channels equally
3. **Progressive thresholding:** Starting at 99.9% of the max brightness, the threshold is progressively lowered through [99.5, 99.0, 98.5, ..., 96.0%] until a connected blob with >= 20 pixels is found. This skips isolated glare artifacts (single bright pixels from lens flare) that pass high thresholds but are too small to be the sun.
4. **Component labeling:** `scipy.ndimage.label()` finds connected components in the binary mask; the largest blob is selected
5. **Center refinement (large blobs, >100px):** For heavily overexposed suns, the blob is uniformly saturated and centroid-based methods are unreliable. Instead, a Gaussian blur is applied to the sum-of-channels luminance within the blob's bounding box, and the peak of the blurred image is used. Sigma scales adaptively: `sigma = max(1, min(blob_radius * 0.12, 5))`, where `blob_radius = sqrt(blob_size / pi)`. The cap at 5 prevents over-smoothing on massive blobs (e.g. hongkong at 163k pixels, radius ~228).
6. **Center refinement (small blobs, <=100px):** Brightness-weighted centroid via `scipy.ndimage.center_of_mass()`
7. **Fallback:** If no blob is found at any threshold, the single brightest pixel is used

Returns `(x, y)` pixel coordinates of the detected sun center.

### 4.2 Camera Calibration

The camera model maps between angular sky coordinates and pixel coordinates using the thin-lens (pinhole) approximation:

**From focal length and sensor dimensions:**

$$\text{FOV}_h = 2 \arctan\left(\frac{\text{sensor\_width\_mm}}{2 \times \text{focal\_length\_mm}}\right)$$

$$\text{FOV}_v = 2 \arctan\left(\frac{\text{sensor\_height\_mm}}{2 \times \text{focal\_length\_mm}}\right)$$

$$\text{pixels\_per\_degree\_az} = \frac{\text{image\_width\_px}}{\text{FOV}_h}$$

$$\text{pixels\_per\_degree\_alt} = \frac{\text{image\_height\_px}}{\text{FOV}_v}$$

Both sensor dimensions and focal length are required because focal length alone is ambiguous without knowing the sensor size (a 50mm lens on full-frame vs. APS-C produces very different fields of view).

### 4.3 Sky-to-Pixel Projection (`sky_to_pixel()`)

The projection maps sky coordinates (altitude, azimuth) to image pixel coordinates relative to the anchor sun position. A critical correction accounts for the convergence of azimuth lines at high altitudes:

$$\Delta x = \Delta\text{az} \times \cos(\bar{a}) \times \text{px\_per\_deg\_az}$$

$$\Delta y = -\Delta\text{alt} \times \text{px\_per\_deg\_alt}$$

where:
- $\Delta\text{az} = \text{target\_az} - \text{anchor\_az}$
- $\Delta\text{alt} = \text{target\_alt} - \text{anchor\_alt}$
- $\bar{a} = (\text{anchor\_alt} + \text{target\_alt}) / 2$ is the mean altitude between anchor and target
- The negative sign on $\Delta y$ accounts for image Y-axis pointing downward
- The $\cos(\bar{a})$ factor corrects for azimuthal foreshortening: at altitude $a$, a circle of constant altitude has circumference $360° \times \cos(a)$, so 1 degree of azimuth subtends $\cos(a)$ times fewer linear degrees than at the horizon

Without this correction, the analemma overlay appears horizontally stretched at high altitudes, breaking the figure-8 shape.

### 4.4 Overlay Rendering

The overlay process:
1. Calculate 365 analemma points at the anchor time-of-day
2. Map each to horizon coordinates (altitude, azimuth)
3. Convert all points to pixel coordinates via `sky_to_pixel()` (no altitude filtering -- points below the horizon are included if they fall within image bounds)
4. Draw connecting line segments between consecutive in-bounds points, breaking the polyline at out-of-bounds gaps to prevent spurious lines across the image
5. Draw dots at each visible position with optional date labels (every N days)
6. Mark the anchor point with a red circle and timestamp annotation
7. Add metadata text overlay (location coordinates, analemma time)
8. Save the composited image

A separate `create_composite_plot()` method generates a 2-panel matplotlib figure with the overlaid image on the left and a sky chart (altitude vs. azimuth scatter) on the right.

---

## 5. Metadata System

### 5.1 Parser (`metadata_parser.py`)

The parser reads `KEY=VALUE` format files with the following rules:
- Lines starting with `#` are comments (skipped)
- Blank lines are skipped
- A separator line containing `--- REFERENCE DATA` stops parsing (everything after is human-readable reference material, not machine-parsed)
- Keys are converted to lowercase with underscores

**Field type conversion:**

| Fields | Type | Notes |
|--------|------|-------|
| `datetime` | `datetime` | Format: `%Y-%m-%d %H:%M:%S` |
| `latitude`, `longitude`, `altitude_m` | `float` | GPS coordinates |
| `focal_length_mm`, `sensor_width_mm`, `sensor_height_mm` | `float` | Camera optics |
| `timezone_offset` | `float` | UTC offset in hours (e.g., -10 for Hawaii) |
| `image_file`, `camera_make`, `camera_model`, `location_name` | `str` | Descriptive metadata |

### 5.2 Image Auto-Detection

If no `IMAGE_FILE` key is present, `load_input_image()` scans the input directory for files with extensions `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.tif` (case-insensitive). If multiple images are found, the first is used with a warning. HEIC files are not supported by PIL.

### 5.3 End-to-End Pipeline

```
input_images/<name>/metadata.txt
        |
        v
  MetadataParser.parse_metadata()
        |
        v
  ImageAnchorer(image, datetime, lat, lon, tz_offset, mode)
        |
        v
  _detect_sun_position() --> calibrate_from_focal_length()
        |
        v
  generate_analemma_points() --> overlay_analemma()
        |
        v
  output/<name>_output/<name>_overlay.png
```

---

## 6. Technologies and Dependencies

| Package | Role | Required |
|---------|------|----------|
| NumPy | Vectorized trigonometry, array operations | Yes |
| Matplotlib | Static plots, composite figures, image rendering | Yes |
| Pillow (PIL) | Image loading, EXIF handling, overlay drawing | Yes |
| Pandas | Data manipulation (optional usage) | Yes |
| Astropy | JPL DE440/441 ephemeris for high-precision mode | Yes |
| SciPy | Connected-component labeling, Gaussian filtering for sun detection | Yes |
| Timezonefinder | IANA timezone lookup from GPS coordinates | Yes |
| Plotly | Interactive hover-enabled scatter plots | Yes |

**CLI tools:** `argparse` for the command-line interface (`analemma_cli.py`), `pathlib` for cross-platform path handling, `datetime` for temporal calculations.

---

## 7. Validation

### 7.1 Unit Tests (`tests/test_calculator.py`)

- **Solstice declinations:** Verify $\delta \approx \pm 23.45°$ at days 172 and 355
- **Equinox declinations:** Verify $\delta \approx 0°$ at days 81 and 264
- **EoT extrema:** Verify the approximate curve matches known peak values
- **Edge cases:** Polar latitudes, equatorial observers, midnight sun conditions

### 7.2 Real-World Datasets

| Dataset | Location | Lat | Camera | Notes |
|---------|----------|-----|--------|-------|
| hongkong | Hong Kong | 22.3 N | Canon PowerShot G10 | Sunset from Ap Lei Chau, TZ auto-detect correct (UTC+8) |
| nigeria | Jos Plateau | 9.8 N | iPhone 14 Plus | Near-equatorial, low sun |
| robert_hawaii | Honolulu | 21.3 N | iPhone 11 | Morning sun, requires `TIMEZONE_OFFSET=-10` |
| raghav | UIUC | 40.1 N | iPhone 16 Pro | Near-sunset, ~240/365 below horizon |
| raghav2 | Oregon | 45.2 N | -- | High sun, noon-ish |
| raghav6 | Houston | 29.8 N | iPhone 16 Pro | Afternoon sun |
| sharjah_sands | UAE | 25.3 N | Nikon D3100 | Desert sunset, analemma extends below horizon |
| brofjorden | Sweden | 58.4 N | -- | Sunset over water |
| cold_canada | Quebec | 46.8 N | -- | Winter morning, uniformly saturated sun blob |
| russia_meadow | Germany | 49.2 N | -- | Large sun glow near horizon |
| hunan | China | 27.0 N | -- | Morning sun |

### 7.3 Mode Comparison

At UIUC (40.1 N, -88.2 W) for year 2025, the maximum differences between approximate and high-precision modes are:
- Declination: ~1.2 degrees (mainly at solstices where the approximate sine wave oversimplifies)
- Equation of Time: ~5.3 minutes (reflecting the limitations of the Spencer 3-term approximation vs. full orbital mechanics)

These differences are consistent with published comparisons between the Spencer approximation and the NOAA solar calculator.

---

## 8. Technical Challenges and Solutions

### 8.1 Timezone Auto-Detection

The naive `round(longitude/15)` formula fails for locations where political timezones differ from geographic longitude bands (Hawaii at -157.8 gives -11 instead of -10, all of China uses +8 despite spanning 60 degrees of longitude, India uses +5.5).

The engine now uses `timezonefinder` + `zoneinfo` to look up the IANA timezone name from GPS coordinates and compute the exact UTC offset for the anchor datetime. This correctly handles DST transitions, half-hour offsets, and political boundaries. Three-tier fallback: explicit `TIMEZONE_OFFSET` metadata field > IANA auto-detection > `round(lon/15)` with warning.

### 8.2 High-Precision EoT Calculation

The original HP mode fell back to the approximate Spencer formula for EoT while using Astropy for declination, defeating the purpose. The fix computes EoT from first principles using Astropy's sun RA and the mean solar longitude $L_0$. Sign convention follows NOAA: $\text{EoT} = (L_0/15 - \text{RA}_\text{sun}) \times 60$ minutes.

### 8.3 Azimuthal Foreshortening in Image Projection

A flat linear projection of azimuth to pixels produces a horizontally stretched overlay at high altitudes because azimuth lines converge toward the zenith. The fix applies a $\cos(\bar{a})$ correction factor to the azimuthal pixel displacement, where $\bar{a}$ is the mean altitude between anchor and target. This models the spherical geometry of the sky dome.

### 8.4 FOV from Focal Length

Focal length alone doesn't determine field of view -- it depends on sensor size. A 50mm lens on full-frame (36mm sensor) gives 40 deg FOV, but the same lens on APS-C (23.5mm sensor) gives 27 deg. Both sensor dimensions and focal length are mandatory in metadata. FOV is computed via $\text{FOV} = 2\arctan(\text{sensor}/2f)$.

### 8.5 Sun Detection Robustness

Simple brightest-pixel approaches fail when the sky has glare artifacts, reflections, or multiple bright regions. The progressive thresholding approach (Section 4.1) handles this by requiring a minimum blob size of 20 pixels, which filters out isolated hot pixels. For large overexposed blobs where the entire region is uniformly saturated (e.g. cold_canada's 411-pixel blob with RGB values 244-246 across all channels), there's no meaningful gradient to locate a "true" center. The Gaussian blur peak is the best available estimate in this case. The adaptive sigma scaling (0.12 * blob_radius, capped at 5) was tuned across 11 test images spanning blob sizes from 411px to 163k px.

### 8.6 EXIF Orientation

Many phone cameras store images in landscape orientation with an EXIF rotation tag. Processing raw pixels without correcting for this produces rotated overlays. `PIL.ImageOps.exif_transpose()` is applied immediately after loading, before any pixel-level operations.

---

## 9. Project Metrics

| Metric | Value |
|--------|-------|
| Core Python modules | 5 (calculator, sky_mapper, plotter, image_anchor, metadata_parser) |
| Utility scripts | 3+ (CLI, demo scripts, examples) |
| Calculation modes | 2 (approximate, high-precision) |
| Visualization types | 6 (sky chart, figure-8, time series, polar, interactive, comparison) |
| Real-world test datasets | 11 (across 8 countries, 5+ camera types) |
| Image formats supported | JPG, JPEG, PNG, GIF, BMP, TIFF |
