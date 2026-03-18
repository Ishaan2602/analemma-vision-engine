# Frontend Design Brainstorm

Design considerations for the Analemma web app UI. The app is a single-page tool: upload a sky photo, enter metadata, get an analemma overlay. No accounts, no navigation maze.

## Design Philosophy

The app does one thing. The design should reflect that -- focused, clear, and not trying too hard. Think of it like a well-made single-purpose tool, not a dashboard.

The personality comes from the content itself: sky photographs and astronomical curves are inherently beautiful. The UI should step back and let the imagery be the star. Dark theme is natural here -- you're working with sky photos.

## Layout Concepts

### Concept A: "Single Column Flow"

A vertical flow, one step at a time. Mobile-first. Each section slides into view as the user completes the previous one.

```
[Hero / upload area]
  Drop a sky photo or click to browse
  
[EXIF auto-fill notification]
  "We found metadata in your image. Check the fields below."

[Metadata form]
  Location: [autocomplete search] or [lat/long manual]
  Date/Time: [pre-filled from EXIF]
  Camera: [auto-detected, sensor sizes filled]
  Focal length: [pre-filled]

[Generate button]
  "Generate Analemma"

[Result viewer]
  [Animated analemma overlaid on photo]
  [Download button]
  [Share? maybe later]
```

Pros: Dead simple. Works on every screen size. Clear progression.
Cons: Lots of scrolling on desktop. Doesn't use wide screens well.

### Concept B: "Split Panel"

Desktop: image on the left (or right), controls on the other side. The image panel stays fixed while the user scrolls through settings. Mobile: collapses to single column.

```
Desktop:
+----------------------------+------------------+
|                            |  Upload photo    |
|     [Sky photo preview     |  Location: ___   |
|      or result with        |  Datetime: ___   |
|      animated analemma]    |  Camera: ___     |
|                            |  [Generate]      |
|                            |  [Download]      |
+----------------------------+------------------+

Mobile:
[Upload photo]
[Form fields]
[Generate]
[Result / animated preview]
[Download]
```

Pros: Image is always visible while editing metadata. Professional feel. Great use of desktop space.
Cons: Slightly more complex CSS. Need to handle the transition from upload state to result state gracefully.

### Concept C: "Wizard / Step Flow"

Multi-step interface. Each step is a full-screen card that transitions to the next.

```
Step 1: Upload your sky photo  [drop zone]
  --> (auto-detect EXIF, fill what we can)
Step 2: Confirm location       [map preview + autocomplete]
Step 3: Confirm camera details [sensor size, focal length]
Step 4: Generating...          [progress animation]
Step 5: Your analemma          [animated result + download]
```

Pros: Focused attention on each step. Great for mobile. Can show explanatory text per step without cluttering.
Cons: More clicks/taps. Users who know what they're doing will be frustrated by forced linearity. Backtracking is annoying.

### Recommendation: Concept B (Split Panel)

Concept B balances desktop utility with mobile simplicity. The fixed image preview is genuinely useful -- you can see the photo while filling in metadata. The mobile collapse to single-column is a solved CSS problem with Tailwind's responsive utilities.

## Color Palette

Given we're working with sky/astronomy imagery:

**Dark theme primary:**
- Background: deep navy/charcoal (#0f172a or #1e293b -- Tailwind slate-900/800)
- Cards/panels: slightly lighter (#1e293b or #334155)
- Primary accent: warm gold/amber (#f59e0b or #fbbf24) -- the color of the sun/analemma curve
- Secondary accent: cool blue (#3b82f6) -- sky tones
- Text: white (#f8fafc) and light gray (#94a3b8)
- Success/active: emerald (#10b981)
- Error: rose (#f43f5e)

**Why dark theme is right:**
- Sky photos look dramatically better on dark backgrounds. A white surrounding area washes out the photo.
- The analemma curve (gold/amber) pops against dark backgrounds.
- Astronomy apps universally use dark themes. Users expect it.
- Dark themes are easier on the eyes for the kind of careful visual inspection this app involves.

**Light theme option (toggle):**
Not for V1. Add later if users request it.

## Typography

Keep it clean. One font family, maybe two weights.

Good options:
- **Inter** -- the go-to for web apps. Clean, highly readable, free. Available from Google Fonts or bundled.
- **JetBrains Mono** -- for metadata values (sensor size, coordinates). Monospace makes numbers align.

Don't overthink this. Inter for everything, JetBrains Mono for technical readouts.

## Key UI Elements

### Upload Area

Large, prominent drop zone. Drag-and-drop + click-to-browse. Show accepted formats. On mobile, the "click to browse" triggers the camera roll picker.

After upload:
- Show image preview immediately
- Show EXIF extraction status ("Found GPS coordinates", "Camera: iPhone 14 Pro", etc.)
- If HEIC: show a brief "Converting for preview..." state, then the JPEG preview
- If no EXIF: show a gentle nudge ("No metadata found -- please fill in the fields below")

### Location Autocomplete

Text input with dropdown suggestions. As the user types, LocationIQ results appear. Selecting a result fills lat/lon fields and shows the location name.

Also show a "Use coordinates instead" toggle for users who already know their lat/lon.

### Sensor Size

Three states:
1. **Auto-detected from EXIF** -- green checkmark, pre-filled, editable
2. **Looked up from camera model** -- blue info icon, pre-filled, editable
3. **Manual entry** -- yellow warning, empty fields with helper text

Show the detection method so users understand why the fields are pre-filled.

### Generate Button

Big, prominent. Disabled until all required fields are filled. Shows a loading state during processing (spinner + "Calculating 365 sun positions...").

### Result Viewer

The main event. Shows the uploaded photo with the animated analemma overlay.

- SVG overlay on top of the image
- Animation plays once on load (figure-8 curve draws itself, then dots appear)
- "Replay animation" button
- Hover/tap individual dots to see the date and altitude
- Download button (saves the static overlay PNG, not the SVG)
- The image + overlay should fill the available space and be zoomable/pannable on mobile

### Sample Gallery

A horizontal scrolling row of thumbnail cards for the sample images. Each card shows:
- Thumbnail of the original photo
- Location name
- A small "CC BY-SA 4.0" or "CC0" badge

Clicking a sample loads it with pre-filled metadata. The user can immediately generate the overlay.

## Responsive Behavior

| Breakpoint | Layout |
|---|---|
| < 640px (mobile) | Single column. Upload -> Form -> Generate -> Result stacked vertically. |
| 640-1024px (tablet) | Single column, but with wider form fields. Image preview smaller. |
| > 1024px (desktop) | Split panel. Image on left (60%), controls on right (40%). |

Tailwind handles this with `lg:` and `md:` prefixes. SvelteKit + Tailwind makes responsive layouts declarative rather than imperative.

## Animation Design

The analemma animation is the visual highlight. Design it to feel like the sun tracing its path across the sky:

1. **Draw phase** (2-3 seconds): The figure-8 curve draws itself using SVG `stroke-dashoffset`. Smooth easing (cubic-in-out). Gold/amber color with slight glow.

2. **Dot phase** (1-2 seconds): After the curve finishes, individual sun positions fade in sequentially along the curve. Small circles. Staggered by 10-20ms each.

3. **Anchor highlight** (0.5 seconds): The dot corresponding to the photo's date pulses and grows slightly larger. Different color (white or bright yellow) to distinguish it.

4. **Labels phase** (1 second): Month labels fade in along the curve.

5. **Interactive state**: After animation completes, hovering any dot shows a tooltip with date and altitude.

Total animation duration: ~5-6 seconds. Long enough to feel satisfying, short enough to not annoy.

Include a "Skip animation" button for repeat users.

## Accessibility

- All form fields labeled properly
- Image alt text for the uploaded photo and overlay
- Keyboard navigation for the form and controls
- Sufficient color contrast (dark theme makes this easier with bright text)
- The SVG overlay elements can have ARIA labels
- "Reduce motion" media query: if the user prefers reduced motion, show the final state directly instead of animating

## Mobile-Specific Considerations

- Touch-friendly tap targets (min 44x44px)
- File input triggers the native camera roll picker on iOS/Android
- HEIC handling (conversion for preview, EXIF extraction)
- Viewport meta tag for proper mobile scaling
- No hover-only interactions -- everything accessible via tap
- Download button uses `<a download>` attribute, which works on both platforms
- Consider a "share" button using the Web Share API (mobile only)
