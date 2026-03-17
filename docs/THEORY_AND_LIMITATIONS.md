# Theory and Limitations

This document describes the theoretical foundations, assumptions, and known limitations of the analemma overlay engine.

---

## 1. Camera Projection Model

### 1.1 Pinhole Camera Assumption

The overlay engine maps sky coordinates (altitude/azimuth) to image pixels using a **pinhole camera model**. The relationship between angular displacement in the sky and pixel displacement in the image is:

$$\text{pixels\_per\_degree} = \frac{\text{image\_dimension\_px}}{\text{field\_of\_view\_deg}}$$

The FOV is derived from focal length and sensor size:

$$\text{FOV} = 2 \arctan\left(\frac{\text{sensor\_dim\_mm}}{2 \times \text{focal\_length\_mm}}\right)$$

This is exact for a geometric pinhole and a good approximation for rectilinear (non-fisheye) lenses at narrow-to-moderate FOV.

### 1.2 Azimuth Compression at High Altitude

One degree of azimuth does not subtend the same angle on the sky at all altitudes. Near the zenith (altitude = 90 deg), lines of constant azimuth converge to a point, just as lines of longitude converge at the Earth's poles. The correction factor is:

$$\Delta x_{\text{px}} = \Delta\text{az} \times \cos(\bar{a}) \times \text{ppd\_az}$$

where $\bar{a}$ is the mean altitude of the anchor and target point. This correction is essential: without it, an analemma near the zenith appears far too wide compared to one near the horizon.

The `cos(altitude)` correction is a first-order approximation. For analemmas spanning a large altitude range (>30 deg), the compression factor changes significantly between the top and bottom of the figure-8, potentially introducing ~1-2 degree errors at the extremes. The engine uses the mean altitude of anchor and target as a midpoint approximation.

### 1.3 Landscape Camera Orientation

The engine assumes the camera is held in normal landscape orientation (horizon roughly horizontal, not tilted up or down significantly). Under this assumption:
- Azimuth differences map to horizontal pixel offsets
- Altitude differences map to vertical pixel offsets (inverted, since pixel y increases downward)

If the camera is tilted up toward the zenith, the mapping between (az, alt) and (x, y) pixels rotates and distorts. For cameras pointed at altitudes above ~70 deg, the simple linear mapping breaks down because the coordinate transform from equatorial-mounted (az/alt) axes to camera-frame (x/y) axes requires a full 3D rotation matrix. The current engine doesn't implement this.

A near-zenith observation (altitude ~70 deg) shows noticeable shape distortion in the overlay compared to the sky chart. This is expected -- a fundamental limitation of the flat-field projection at extreme altitudes.

---

## 2. Timezone Handling

### 2.1 IANA Database (current implementation)

The engine uses the `timezonefinder` library to look up the IANA timezone name (e.g., "America/Chicago") from GPS coordinates, then uses Python's `zoneinfo` module to determine the exact UTC offset for the given reference datetime. This correctly handles:

- Political timezone boundaries: Hawaii is UTC-10 (not UTC-11 from `round(lon/15)`)
- DST transitions: UIUC in September gets UTC-5 (CDT), while in January it would get UTC-6 (CST)
- Half-hour offsets: India gets UTC+5:30 (Asia/Kolkata)
- Non-standard offsets: Western China uses UTC+6 (Asia/Urumqi) or UTC+8 (Asia/Shanghai) depending on the political boundary

### 2.2 Limitation: DST and Year-Long Analemma

The engine calculates the analemma for a fixed clock time throughout the year. The timezone offset used is determined from the **anchor datetime** (the date the photo was taken). This means:

- If the photo was taken during DST, the entire analemma is computed with the DST offset
- In reality, the sun positions in the non-DST months would correspond to a different clock time (one hour earlier/later)

This isn't a bug -- it reflects the physical question "where would the sun be at this clock time every day of the year?" The DST-vs-standard ambiguity is inherent to clock time; the engine uses whatever offset applies at the reference date.

### 2.3 Fallback Behavior

If `timezonefinder` is not installed, the engine falls back to `round(longitude / 15)`, which is correct for most locations but fails for political exceptions. A warning is issued in this case.

---

## 3. Sun Detection (Computer Vision)

### 3.1 Current Algorithm

The CV pipeline uses a multi-stage approach to find the sun:

1. EXIF orientation correction via `PIL.ImageOps.exif_transpose()`
2. Grayscale conversion using `max(R, G, B)` per pixel (preserves saturation better than luminance-weighted average)
3. Progressive thresholding: starts at 99.9% of max brightness, lowers through [99.5, 99, 98.5, ..., 96%] until a blob with >= 20 pixels is found. This skips isolated glare artifacts that are bright but tiny.
4. Connected component labeling (`scipy.ndimage.label`) selects the largest blob
5. Brightness-weighted centroid of the blob pixels, using `max(R,G,B)` as weights
6. Fallback: brightest pixel if no blob is found

### 3.2 Requirements and Failure Modes

- Without scipy, the fallback uses simple brightness averaging of all pixels above threshold, which is less robust
- When the sun is heavily overexposed, the bright region may be very large and oddly shaped, shifting the centroid
- Lens flare or specular reflections (Hong Kong harbor water, Robert Hawaii clouds) can create bright non-sun features that confuse the detector
- If the sun is behind clouds or haze (Nigeria sunset), the effective "sun" is a diffuse glow rather than a sharp disk
- The algorithm picks the largest blob, which may not always be the sun (a sun reflection in water could exceed the sky sun in size)

### 3.3 Override

Users can provide explicit `sun_pixel=(x, y)` coordinates to bypass auto-detection.

---

## 4. FOV and Calibration Accuracy

### 4.1 Focal Length from EXIF

The engine reads focal length from image EXIF metadata or the metadata.txt file. For phones, this is the **35mm equivalent focal length**, which requires knowing the crop factor:

$$f_{\text{actual}} = \frac{f_{35\text{mm}}}{\text{crop\_factor}}$$

The metadata.txt format expects the actual focal length and actual sensor dimensions. If the user provides 35mm-equivalent values with full-frame sensor dimensions, the FOV calculation will be correct, but it is a common source of error.

### 4.2 Lens Distortion

Real lenses, especially wide-angle and ultrawide lenses (iPhone ultrawide = 13mm equivalent), exhibit barrel distortion. The pinhole model does not account for this. Effect:
- Points near image edges appear closer to center than the pinhole model predicts
- Analemma overlay near edges will be slightly too far from center

For standard (non-ultrawide) lenses at moderate FOV (<60 deg), the error is typically <1%.

---

## 5. Known Shape Distortions

### 5.1 High-Altitude Analemmas (near zenith)

At observation times where the sun transits near the zenith (tropical latitudes at solar noon), the `cos(altitude)` azimuth compression is extreme. A 1-degree azimuth change at altitude 80 deg produces only `cos(80) = 0.17` degrees of apparent angular separation. This means:
- The sky chart (plotted in degrees) shows a wide figure-8 in azimuth
- The overlay (plotted in pixels) shows a much narrower figure because each degree of azimuth maps to very few pixels

This is physically correct behavior -- the projection IS different near the zenith -- but it can appear as a "shrunk" or "slim" overlay compared to the sky chart.

### 5.2 Impact of Incorrect Timezone

A 1-hour timezone error shifts the analemma by ~15 degrees in azimuth. This can push the anchor point to a completely different part of the image. The IANA-based detection eliminates this class of error for all supported locations.

### 5.3 Large Altitude Span

For sun positions that are far from the anchor altitude, the `cos(mean_altitude)` approximation for azimuth compression becomes less accurate. The error is proportional to:

$$\epsilon \propto \Delta\text{az} \times \left|\sin(\bar{a})\right| \times \frac{\Delta\text{alt}}{2}$$

For a typical analemma with 20 deg altitude span and 30 deg azimuth span at altitude 30 deg, this error is under 0.5 deg.

---

## 6. Precision Modes

### 6.1 Approximate (Spencer 1971)

Uses empirical Fourier series for declination and EoT. Accuracy:
- Declination: max error ~1.2 deg (compared to Astropy)
- EoT: max error ~5.3 min (compared to Astropy)

Sufficient for qualitative visualization but can produce noticeable position errors in overlays.

### 6.2 High-Precision (Astropy/JPL DE440)

Uses JPL DE440 planetary ephemeris via Astropy. Accuracy:
- Position errors < 0.001 deg (sub-arcsecond)
- Requires Astropy installation and internet access for ephemeris download on first use

This mode is recommended for all overlay applications.

---

## 7. Assumptions Summary

| Assumption | Impact if Violated | Severity |
|---|---|---|
| Camera is landscape-oriented, roughly level | Overlay shape and position distorted | High for tilted cameras |
| Pinhole camera (rectilinear lens) | Edge distortion uncompensated | Low-Medium |
| Focal length from metadata is correct | Overlay scale wrong throughout | High |
| Sun is visible and brightest object | Auto-detection fails, falls back | Medium |
| Observer altitude negligible | Horizon elevation shifted | Negligible (<0.1 deg) |
| Atmospheric refraction ignored | ~0.5 deg error near horizon | Low |
| Earth's orbit doesn't change year-to-year | Year-specific perturbations missed | Negligible |
| DST offset fixed to anchor date | Clock time ambiguity in DST regions | Design choice |
