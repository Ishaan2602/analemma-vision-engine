# CV Sun Detection - Debugging Log

This file tracks all iterations of the sun-detection refinement in `image_anchor.py`.
The function under test is `ImageAnchorer._detect_sun_position()`.

---

## Problem Images

Three images have proven difficult for automatic sun detection:

| Image | Blob size | Threshold | Characteristics |
|-------|-----------|-----------|-----------------|
| cold_canada | 411 px | 0.96 | Small blob (52x25), uniformly bright (min_ch 242-246). At 0.999, only 1 random glare pixel at (928,437). Real sun blob only appears at 0.96. Glow extends asymmetrically upward (centroid drifts from y=230 at 0.96 to y=200 at 0.80). |
| russia_meadow | 5425 px | 0.999 | Large sunset glow blob. Colored (not uniformly white). Centroid at (568, 325). |
| brofjorden | 17977 px | 0.999 | Very large blob. Nearly all white (10329/17977 px at min_ch=255). Second blob below = sun reflection on water. |

**Approved positions** (user-verified):
- russia_meadow: **(570, 335)** -- approved at Round 10, confirmed at Round 12
- brofjorden: **(1051, 341)** -- accepted as-is ("hard to deal with")
- cold_canada: best so far is **(750, 235)** at Round 12, but user says overlay still at (-0.2, -0.9)

---

## Diagnostic Data: cold_canada

### Blob structure
- At 0.96 threshold: 411px, bbox x=[724-775] y=[214-238], 52w x 25h
- Centroid: (749.2, 230.2)
- Blob radius: 11.4 px
- Min channel: nearly uniform (242-246 across entire blob)
- All weighted centroids (luminance, max-ch, min-ch, lum^2, lum^4) converge to (749.2, 230.2)
- Erosion to near-collapse (iteration 5, 13px remaining): centroid (747.2, 229.7)

### Vertical brightness profile at x=749
```
y=228-231: sum=735 (brightest tied)
y=232:     sum=732
y=233:     sum=735
y=234-236: sum=738 (peak brightness)
y=237:     sum=735
y=238:     sum=732
```
The actual brightness peak is at y=234-236, NOT at the blob centroid y=230.

### Glow asymmetry (threshold vs centroid)
```
0.960:    411px, centroid=(749, 230)
0.950:   1486px, centroid=(751, 223)  -- glow extends upward
0.940:   3256px, centroid=(755, 213)  -- significantly higher
0.920:   5999px, centroid=(758, 201)
0.800:  13314px, centroid=(758, 200)
```
The glow halo extends much more upward (sky) than downward (toward horizon), pulling the centroid up. The actual sun disk center is near the bottom of the blob.

### Gaussian blur sigma sweep (luminance, cropped region)
```
sigma=1:   peak=(750, 235)  <-- closest to brightness peak
sigma=1.5: peak=(750, 235)
sigma=2:   peak=(746, 233)
sigma=2.5: peak=(748, 233)
sigma=3:   peak=(749, 232)
sigma=4:   peak=(757, 232)
sigma=5:   peak=(756, 230)  <-- pulled toward glow center
sigma=8:   peak=(754, 225)
sigma=10:  peak=(754, 221)
```
Low sigma captures the actual brightness peak at y=235. Higher sigma smooths into the upward glow.

### Full-image Gaussian blur peaks
```
sigma=5:  (756, 230)
sigma=10: (754, 221)
sigma=15: (755, 212)
sigma=30: (758, 201)  -- converges to glow centroid
```

### Masked luminance Gaussian blur (zero outside blob)
```
sigma=1:   (745, 232)
sigma=1.5: (739, 227)  -- unstable
sigma=2:   (763, 233)  -- unstable
sigma=3:   (762, 233)
sigma=5:   (758, 233)
```
Masking to blob region produces unstable results at low sigma due to edge effects.

---

## Iteration History

### Round 1 -- Gaussian blur sigma=10 + threshold 0.995
- Approach: Heavy blur to smooth out glare, high threshold
- cold_canada: fixed (found sun, not glare pixel)
- Other images: pulled off-center
- Verdict: too much blur for large blobs

### Round 2 -- Two-pass (blur locate, original centroid)
- Approach: Use blur to find region, then centroid on original
- Result: still pulled off-center
- Verdict: abandoned

### Round 3 -- Windowed two-pass (blur, 80px crop, 0.999 threshold)
- Approach: Blur to locate, crop 80px window, re-threshold at 0.999
- Result: partial improvement
- Verdict: not reliable enough

### Round 4 -- Light blur peak (sigma=3 argmax)
- Approach: Gaussian blur sigma=3, take argmax
- Result: BROKE hongkong and robert_hawaii
- Verdict: reverted immediately

### Round 5 -- Revert to single-pass 0.999 + min blob 5px
- Approach: Back to basics
- Result: cold_canada back to glare pixel at (928, 437)
- Verdict: baseline, need different approach for cold_canada

### Round 6 -- Min blob 20px + core threshold 0.9999
- Approach: Increase min blob size to 20px, add inner core threshold at 0.9999
- Result: All ran. cold_canada still on glare. russia_meadow in corner. brofjorden off.
- Verdict: core threshold useless (blob pixels all saturated)

### Round 7 -- Progressive threshold (0.999->0.96) + erosion to near-collapse
- Approach: Step through thresholds until blob >= 20px found. Erode blob until near-collapse, take centroid.
- cold_canada: FIXED (749, 230) -- found actual sun at 0.96 threshold
- russia_meadow: (577, 306) -- shifted too far up (erosion overshot)
- brofjorden: (1053, 341) -- reasonable
- Verdict: progressive threshold is key. Erosion overshoots for large colored blobs.

### Round 8 -- Erosion to 10% remaining
- Approach: Erode until 10% of blob remains instead of near-collapse
- russia_meadow: (567, 320) -- still not centered enough
- Verdict: erosion approach fundamentally problematic for non-uniform blobs

### Round 9 -- Min-channel (whitest pixels) centroid
- Approach: Weight centroid by minimum RGB channel (whiter = more likely sun disk)
- russia_meadow: (587, 322) -- off to right
- brofjorden: (1056, 325) -- barely changed (blob is nearly all white, min-ch=255)
- Verdict: min-channel doesn't differentiate in nearly-white blobs

### Round 10 -- Gaussian blur sigma=5 on luminance peak
- Approach: Sum all RGB channels for luminance, Gaussian blur sigma=5 in cropped blob region, take argmax
- cold_canada: (756, 230) -- user says (-0.2, -0.9), still too high
- **russia_meadow: (570, 335) -- USER APPROVED** (-0.4, 0.2)
- brofjorden: (1052, 347) -- accepted
- Verdict: sigma=5 works perfectly for large blobs. Too much smoothing for small blobs.

### Round 11 -- Adaptive sigma (blob_radius * 0.15, clamped [2,8])
- Approach: Scale sigma with blob size. Small blobs get tight focus, large blobs get smoothing.
- cold_canada: (746, 233) at sigma=2.0 -- slight improvement (3px lower)
- russia_meadow: (573, 339) at sigma=6.2 -- shifted 3px right, 4px lower from approved
- brofjorden: (1051, 341) at sigma=8.0
- Verdict: sigma=2 still too much for cold_canada's small blob. russia_meadow slightly drifted.

### Round 12 -- Sigma multiplier 0.12, clamp [1,8] (CURRENT -- saved state)
- Approach: `sigma = max(1, min(blob_radius * 0.12, 8))`
- cold_canada: (750, 235) at sigma=1.37 -- captures brightness peak at y=235
- **russia_meadow: (570, 335) at sigma=5.0 -- exactly the approved position**
- brofjorden: (1051, 341) at sigma=8.0 -- unchanged
- User says: cold_canada still at (-0.2, -0.9). russia_meadow and brofjorden are good.

**Sigma values by image:**
| Image | Blob radius | sigma (0.12 * r) | Clamped |
|-------|------------|-------------------|---------|
| cold_canada | 11.4 | 1.37 | 1.37 |
| russia_meadow | 41.6 | 4.99 | 4.99 |
| brofjorden | 75.6 | 9.07 | 8.0 |

---

## Current State (Round 12 -- saved baseline)

The implementation in `image_anchor.py` `_detect_sun_position()`:
1. Progressive thresholding: 0.999 down to 0.96, find blob >= 20px
2. For large blobs (>100px): Gaussian-blurred luminance peak with adaptive sigma
3. Sigma = max(1, min(blob_radius * 0.12, 8)) where blob_radius = sqrt(blob_size/pi)
4. For small blobs (<=100px): weighted centroid using gray intensity
5. Fallback: brightest pixel

---

## Analysis: Why cold_canada is still off

The user reports (-0.2, -0.9) at (750, 235). This means the overlay curve appears
about 0.9 sun radii too high relative to the visible sun disk.

From the brightness profile, (750, 235) IS at the peak brightness within the blob.
The blob itself spans y=[214-238], with the brightness peak at y=234-236.

Possible explanations for the persistent offset:
1. **The blob at 0.96 threshold does not capture the full sun disk.** The actual sun disk may extend below y=238. At lower thresholds (0.95), the blob extends to y=240.
2. **The brightness peak within the blob may not be the geometric center of the sun disk.** The sun near the horizon has atmospheric refraction that shifts brightness upward relative to geometric center.
3. **The coordinate mapping may have a systematic error** for this particular geometry (low solar altitude, specific focal length, specific sensor size).
4. **The overlay anchor point calculation has a slight error** in how it maps pixel position to alt/az.

### What we've tried
- Every reasonable centroid method (unweighted, luminance-weighted, min-channel-weighted, power-weighted, erosion-based)
- Gaussian blur at every sigma from 1 to 10
- Masked vs unmasked blur
- The results are constrained: all methods give x=746-756, y=225-235

### Remaining options
A. **Lower the threshold further** (e.g., 0.95 or 0.94) to capture more of the sun disk, then find its centroid. Risk: may capture non-sun glow.
B. **Use a different blob entirely** -- look for circular structures specifically.
C. **Apply a small correction offset** based on blob characteristics (e.g., shift toward bottom of blob by some fraction).
D. **Accept the current result** -- the offset is small (< 1 sun radius) and may be inherent to the image/geometry.
