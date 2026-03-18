# Analemma Animation with Keyframes

Research for the Analemma web frontend. The goal: animate the figure-8 analemma curve being "drawn" over the user's sky photograph, like an invisible pen tracing the sun's yearly path.

## Current Backend Architecture

The engine's `ImageAnchorer` class does everything in one shot:

1. `generate_analemma_points()` calculates 365 sun positions (one per day at the same clock time) and maps each to pixel coordinates on the uploaded photo. Returns a list of dicts, each containing `altitude`, `azimuth`, `pixel_x`, `pixel_y`, `date`, and other sky data.

2. `overlay_analemma()` takes those points and uses Pillow's `ImageDraw` to render dots + connecting lines + date labels + the anchor highlight directly onto a copy of the photo. Saves the result as a PNG.

The output is a single static PNG with everything baked in. No intermediate data is exposed to the frontend.

---

## Animation Approaches Compared

### Approach A: SVG Path Animation (Recommended)

The analemma curve is a smooth figure-8. Represent it as an SVG `<path>`, overlay it on the image, and animate the path being drawn using the stroke-dasharray/stroke-dashoffset technique.

**How it works:**

1. Backend returns the analemma curve as JSON: an array of `{x, y, date, altitude, azimuth}` points in pixel coordinates, plus the image dimensions and the anchor point.
2. Frontend loads the original image as the background.
3. Frontend constructs an SVG `<path>` from the point array (using a smooth curve through the points -- either a polyline or a cubic bezier spline).
4. The path's `stroke-dasharray` is set to the total path length. `stroke-dashoffset` starts at the total length (invisible) and animates to 0 (fully drawn).

**Svelte's built-in `draw` transition:**

Svelte has a first-class `transition:draw` that does exactly this. It works on any SVG element that has a `getTotalLength()` method -- `<path>`, `<polyline>`, `<circle>`, `<line>`, `<rect>`.

```svelte
<script>
  import { draw } from 'svelte/transition'
  let visible = false
</script>

<svg>
  {#if visible}
    <path
      d={pathData}
      transition:draw={{ duration: 3000, easing: cubicInOut }}
      stroke="gold"
      stroke-width="3"
      fill="none"
    />
  {/if}
</svg>
```

The transition accepts:
- `delay`: ms before starting
- `speed`: pixels per second (alternative to duration)
- `duration`: total ms, or a function `(pathLength) => ms`
- `easing`: any Svelte easing function

**Layering SVG over the photo:**

The SVG is positioned absolutely on top of the image. Both share the same container with `position: relative`. The SVG's `viewBox` matches the image's pixel dimensions.

```svelte
<div class="overlay-container" style="position: relative;">
  <img src={photoUrl} alt="Sky photo" />
  <svg viewBox="0 0 {imageWidth} {imageHeight}"
       style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    <!-- analemma path here -->
  </svg>
</div>
```

This approach is resolution-independent -- the SVG scales with the image at any viewport size.

**Dots and labels:**

In addition to the path, each sun position can be a small SVG `<circle>`. These can be animated to appear sequentially using staggered `fade` or `scale` transitions. Date labels are SVG `<text>` elements.

**Pros:**
- Clean, semantic markup. Accessible (SVG elements can have ARIA labels).
- Resolution-independent -- looks sharp at any zoom level.
- Svelte's `draw` transition makes this a near-zero-effort animation.
- Small payload. The path data (365 points as JSON) is ~10-15 kB. Compared to a 2-5 MB overlay PNG.
- The user can interact with points (hover for date/altitude info) since they're real DOM elements.
- Easy to restyle (colors, widths, opacity) without regenerating anything on the server.

**Cons:**
- Must construct SVG path data from the point array. This is straightforward (join points with `L` commands for a polyline, or compute control points for a smooth curve).
- Complex visual effects (glow, bloom) are harder in SVG than Canvas.
- For very large numbers of elements (thousands of dots + labels), SVG DOM performance degrades. But we're at ~365 points, well within the comfortable range.

**Verdict: This is the recommended approach.** It's the simplest, most maintainable, best-performing option for this use case. Svelte's `draw` transition makes it almost trivial.

---

### Approach B: Canvas-Based Animation

Use HTML5 `<canvas>` layered on top of the image. Draw the curve incrementally with `requestAnimationFrame`.

**How it works:**

1. Backend returns the same JSON point array.
2. A `<canvas>` element is sized to match the image and positioned on top of it.
3. An animation loop draws the curve progressively: on each frame, draw one or more additional line segments.

```js
let currentIndex = 0
function animate() {
  if (currentIndex >= points.length) return
  ctx.beginPath()
  ctx.moveTo(points[currentIndex - 1].x, points[currentIndex - 1].y)
  ctx.lineTo(points[currentIndex].x, points[currentIndex].y)
  ctx.stroke()
  currentIndex++
  requestAnimationFrame(animate)
}
```

**Pros:**
- Full pixel-level control. Easy to add glow effects (`ctx.shadowBlur`), gradients, or particle trails.
- Performant for large numbers of elements (Canvas doesn't create DOM nodes).
- Good for complex visual effects that SVG can't do easily.

**Cons:**
- Not resolution-independent. Canvas resolution is fixed at creation time. Needs manual handling of `devicePixelRatio` for retina displays. Resizing the window requires redrawing.
- No built-in animation primitives. You write the animation loop manually.
- No interactivity for individual points without hit-testing math (can't hover a Canvas pixel to get the date).
- In Svelte, there's no built-in Canvas animation helper. You'd write a `use:action` or `onMount` with manual lifecycle management.
- More code than the SVG approach for the same result.

**Verdict: Viable but unnecessary.** Canvas is the right choice when you need complex visual effects or thousands of animated elements. For a figure-8 curve with ~365 points, SVG is simpler and better.

---

### Approach C: CSS Keyframe Animation (Dots Only)

Animate individual dots appearing one by one using CSS `@keyframes` with staggered `animation-delay`.

**How it works:**

Each sun position is a small `<div>` (or SVG `<circle>`) absolutely positioned on the image. CSS makes each dot appear with a delay proportional to its index:

```css
.dot {
  opacity: 0;
  animation: appear 0.1s forwards;
}
.dot:nth-child(1) { animation-delay: 0ms; }
.dot:nth-child(2) { animation-delay: 20ms; }
/* ... 365 rules, or use inline styles */
```

**Pros:**
- Pure CSS, no JavaScript animation code.
- Hardware-accelerated opacity transitions.

**Cons:**
- **No connecting line.** You can animate dots appearing, but you can't animate a line being drawn with pure CSS. The line *is* the key visual element.
- 365 individually positioned elements with inline styles is messy.
- CSS `animation-delay` on 365 elements creates a lot of style recalculation.
- Svelte's `each` block with `transition:fade` and staggered delays is cleaner than raw CSS, but still doesn't solve the line problem.

**Verdict: Insufficient.** The connecting curve is the centerpiece of the animation. CSS keyframes can enhance (staggered dot appearance) but can't replace the path-drawing effect. Use CSS for dot appearance *alongside* SVG path animation, not instead of it.

---

### Approach D: Animation Libraries

#### GSAP (GreenSock Animation Platform)

- **Bundle:** ~25 kB gzip (core)
- **License:** Free for most uses (Standard License). The `DrawSVGPlugin` is paid (Club GreenSock), but you don't need it -- core GSAP can animate `strokeDashoffset` directly.

GSAP is the industry standard for web animation. It handles the `stroke-dashoffset` animation the same way Svelte's `draw` does, but works in any framework.

```js
const path = document.querySelector('.analemma-path')
const length = path.getTotalLength()
gsap.fromTo(path,
  { strokeDasharray: length, strokeDashoffset: length },
  { strokeDashoffset: 0, duration: 3, ease: 'power2.inOut' }
)
```

**When to use:** If you're using React or Vue (which lack built-in SVG draw transitions) and want a polished animation with timeline control, staggering, and easing. GSAP's timeline feature lets you sequence the path draw, then dot reveals, then label fades, as a choreographed sequence.

**With Svelte:** Unnecessary. Svelte's `draw` transition plus its built-in easing functions cover the same ground with zero extra dependencies.

#### Motion One

- **Bundle:** ~3.5 kB gzip
- **Framework-agnostic, uses the Web Animations API**

Lighter than GSAP. Can animate `strokeDashoffset` via the Web Animations API. Good choice for React/Vue if you want the smallest possible bundle.

#### Framer Motion

- **React-only.** ~40 kB gzip.
- Has `motion.path` with `pathLength` animation. Works well.
- Irrelevant if using Svelte.

#### Lottie

- **For pre-authored animations.** You'd create the animation in After Effects, export as Lottie JSON, and play it on the frontend.
- Wrong tool here. The analemma curve is data-driven (different for each photo), not pre-authored.

**Verdict on libraries:** If using Svelte, no animation library needed. If using React, GSAP or Framer Motion. If using Vue, GSAP or Motion One. The SVG stroke-dashoffset technique works the same regardless of how you trigger the animation.

---

## Backend Changes Needed

The current engine returns a completed PNG overlay. For client-side animation, the backend needs to also return the raw analemma data as JSON.

### New API Endpoint: `/process` (Modified)

Currently the backend vision is:
```
POST /process
  Input: image + metadata
  Output: overlay PNG
```

For animation support, return both the original image (or a URL to it) and the curve data:

```
POST /process
  Input: image + metadata
  Output: JSON response:
  {
    "original_image_url": "/images/{id}/original.jpg",
    "overlay_image_url": "/images/{id}/overlay.png",    // static overlay, still available
    "analemma_data": {
      "image_width": 4032,
      "image_height": 3024,
      "anchor_point": {
        "pixel_x": 1845,
        "pixel_y": 1230,
        "date": "2024-09-02",
        "altitude": 52.3,
        "azimuth": 245.1
      },
      "points": [
        {
          "pixel_x": 1820,
          "pixel_y": 1180,
          "date": "2024-01-01",
          "altitude": 55.1,
          "azimuth": 243.8
        },
        // ... 364 more points
      ],
      "metadata": {
        "latitude": 22.3,
        "longitude": 114.2,
        "timezone": "Asia/Hong_Kong",
        "time_of_day": "16:20"
      }
    }
  }
```

### Changes to the Engine

The data is already computed. `generate_analemma_points()` in `ImageAnchorer` returns exactly the list of dicts we need. The changes are:

1. **Extract `generate_analemma_points()` as a standalone operation** that can be called without rendering the overlay. Currently it's called inside `overlay_analemma()` with no way to get the data separately. This is a small refactor -- make the points available as a public method (it already is) and add a method like `get_analemma_json()` that returns the data in a serializable format.

2. **Add a JSON-compatible serialization method:**
```python
def get_analemma_json(self) -> dict:
    """Return analemma data as a JSON-serializable dict."""
    points = self.generate_analemma_points()
    return {
        'image_width': self.image_width,
        'image_height': self.image_height,
        'anchor_point': {
            'pixel_x': self.sun_pixel[0],
            'pixel_y': self.sun_pixel[1],
            'date': self.anchor_datetime.strftime('%Y-%m-%d'),
            'altitude': self.anchor_data['altitude'],
            'azimuth': self.anchor_data['azimuth'],
        },
        'points': [
            {
                'pixel_x': p['pixel_x'],
                'pixel_y': p['pixel_y'],
                'date': p['date'].strftime('%Y-%m-%d'),
                'altitude': p['altitude'],
                'azimuth': p['azimuth'],
            }
            for p in points
        ],
    }
```

3. **Keep the static overlay as an option.** The PNG overlay is still useful for:
   - Direct download (users want a single image file they can share)
   - Social media sharing (can't share an interactive SVG on Instagram)
   - Non-JS contexts (email previews, thumbnails)
   
   The API should return both the overlay PNG URL and the JSON data.

4. **SVG path generation (optional, could be client-side).** The backend could generate the SVG `d` attribute directly from the pixel coordinates. But it's simpler to let the frontend construct the path from the point array. A polyline is just:
   ```
   M x0,y0 L x1,y1 L x2,y2 ...
   ```
   Or for a smooth curve, the frontend can use cardinal spline interpolation.

### Points to Filter

The current engine filters out points below the horizon and outside the image bounds. The JSON data should include this filtering too -- only return points that would be visible in the image. The frontend shouldn't have to know about coordinate systems or image bounds.

---

## Recommended Implementation Plan

### Architecture

```
[Backend]                          [Frontend (Svelte)]
                                   
POST /process                      
  -> detect sun                    
  -> calculate analemma            
  -> render overlay PNG            -> Static overlay download
  -> serialize point data          -> JSON response
                                     |
                                     v
                                   [Image component]
                                     Original photo as <img>
                                     SVG overlay with analemma path
                                     transition:draw for animation
                                     Hover tooltips on points
                                     "Play" button to trigger animation
                                     "Download overlay" button -> static PNG
```

### Frontend Components

1. **`AnalemmaOverlay.svelte`** -- main component
   - Receives `imageUrl`, `analemmaData` as props
   - Contains the `<img>` + `<svg>` overlay stack
   - Constructs the SVG path from point data
   - Controls animation state (play/pause/reset)

2. **SVG structure:**
   ```svelte
   <svg viewBox="0 0 {data.image_width} {data.image_height}">
     <!-- Connecting curve -->
     {#if showCurve}
       <path d={curvePath} transition:draw={{ duration: 3000 }}
             stroke="gold" stroke-width="3" fill="none" opacity="0.8" />
     {/if}
     
     <!-- Sun position dots (staggered reveal) -->
     {#each visiblePoints as point, i}
       <circle cx={point.pixel_x} cy={point.pixel_y} r="5"
               fill="yellow" stroke="black" stroke-width="1"
               transition:scale={{ delay: i * 20 }} />
     {/each}
     
     <!-- Anchor point (highlighted) -->
     <circle cx={data.anchor_point.pixel_x} cy={data.anchor_point.pixel_y}
             r="10" fill="red" stroke="white" stroke-width="2" />
     
     <!-- Date labels (every 30 days) -->
     {#each labeledPoints as point}
       <text x={point.pixel_x + 12} y={point.pixel_y}
             fill="white" font-size="12">{point.dateLabel}</text>
     {/each}
   </svg>
   ```

3. **Animation sequence:**
   - User clicks "Show Analemma"
   - Path draws itself over 3 seconds (Svelte `draw` transition)
   - After path is complete, dots appear with staggered `scale` transitions
   - Labels fade in last
   - Anchor point pulses or glows to draw attention

### Constructing the SVG Path

The points from the backend are ordered chronologically (Jan 1 through Dec 31). To draw a smooth figure-8:

**Option 1: Polyline (simplest)**
```js
const d = `M ${points[0].pixel_x},${points[0].pixel_y} ` +
  points.slice(1).map(p => `L ${p.pixel_x},${p.pixel_y}`).join(' ')
```
This produces a segmented line with visible corners between days. Fine for 365 points (the spacing is close enough to look smooth).

**Option 2: Catmull-Rom spline (smoother)**
Convert the point sequence to a smooth SVG cubic bezier curve using Catmull-Rom to bezier conversion. This produces a visually smoother curve. There are small (~50 line) JS functions that do this conversion. Worth doing if the polyline looks too jagged.

---

## Performance Considerations

- **Data size:** 365 points with 5 fields each: ~10 kB as JSON. Negligible compared to the image.
- **SVG rendering:** 365 `<circle>` elements + 1 `<path>` + ~12 `<text>` labels = ~380 DOM nodes. Well within the SVG performance comfort zone (problems start at ~5000+ nodes).
- **Animation:** The `stroke-dashoffset` animation is GPU-accelerated in all modern browsers. Smooth 60fps even on phones.
- **Memory:** The original image displayed as `<img>` uses the same memory as it would for a static overlay. The SVG adds negligible overhead.
- **Compared to the static PNG approach:** The animated approach actually uses *less* bandwidth. The JSON data (~10 kB) is much smaller than a second full-resolution PNG overlay (~2-5 MB).

---

## Summary: What to Build

| Component | Implementation |
|---|---|
| Animation technique | SVG path with `stroke-dashoffset` animated via Svelte's `draw` transition |
| Image display | Original photo as `<img>`, SVG positioned absolutely on top |
| Backend data format | JSON array of `{pixel_x, pixel_y, date, altitude, azimuth}` + image dimensions + anchor point |
| Backend change | Add `get_analemma_json()` method to `ImageAnchorer`; keep `overlay_analemma()` for static PNG download |
| Curve smoothing | Start with polyline, upgrade to Catmull-Rom spline if it looks jagged |
| Interactivity | Hover tooltips on dots showing date + altitude + azimuth |
| Static fallback | PNG overlay still generated and available for download |
| Animation library needed | None (Svelte built-in) |
