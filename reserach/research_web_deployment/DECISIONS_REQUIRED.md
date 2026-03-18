# Decisions Required Before Planning

Everything below needs your input before we move to detailed planning. Each question references the specific research file where the options are analyzed in depth.

---

## 1. Frontend Framework

**Question:** Which frontend framework do you want to use?

| Option | Learning Curve | Best Feature for Us | Ecosystem Size |
|---|---|---|---|
| **Svelte/SvelteKit** | Lowest | Built-in `draw` transition for analemma animation | Smallest |
| **Vue 3 + Vite** | Low | VueUse composables, larger community | Medium |
| **React + Vite** | Medium | Largest ecosystem, most career-applicable | Largest |

The research recommends **Svelte** for this project specifically because of the built-in SVG path animation and the fact that this is a single-page tool, not a complex app. Vue is the strong runner-up. React works but adds complexity you won't use.

See: `research_frontend_frameworks/recommendations.md`

**Your answer:**

---

## 2. Backend Framework

**Question:** FastAPI or Flask for the Python API?

| Option | Why Consider |
|---|---|
| **FastAPI** (recommended) | Auto-generated API docs, typed validation, modern async foundation |
| **Flask** | Simpler, you might already know it, slightly less learning |

The research recommends FastAPI. The overhead compared to Flask is minimal (an afternoon of learning), and the auto-generated Swagger UI is genuinely useful during development.

See: `research_backend_framework/recommendation.md`

**Your answer:**

---

## 3. Deployment Configuration

**Question:** Which deployment setup do you want to start with?

| Config | Frontend | Backend | Domain | Monthly Cost | Free Duration |
|---|---|---|---|---|---|
| **Config 1** | DO App Platform | DO App Platform (2 GB) | Name.com | $25 (credit) | ~8 months |
| **Config 2** (recommended) | Vercel (free) | DO App Platform (2 GB) | Name.com | $25 (credit) | ~8 months |
| **Config 3** | Heroku (bundled) | Heroku Basic (512 MB) | Namecheap | $7 (credit) | 24 months |
| **Config 4** | Vercel (free) | Fly.io (2 GB) | Name.com | $2-11 | Indefinite |

Config 2 is recommended for the best developer experience. Config 3 lasts longest but 512 MB RAM is risky with our dependencies. Config 4 is best long-term but costs a few dollars/month from day one.

See: `research_deployment/recommendations.md`

**Your answer:**

---

## 4. Domain Name

**Question:** What domain do you want?

You can get one free domain from the student pack:
- **Name.com**: free `.dev`, `.app`, `.live`, `.studio`, `.software` for 1 year
- **Namecheap**: free `.me` for 1 year

Some ideas (check availability):
- `analemma.dev`
- `analemma.app`
- `analemma.live`
- `analemma.studio`
- `solaranalemma.dev`

**Your answer:**

---

## 5. Geocoding API

**Question:** Which geocoding service for location autocomplete?

| Option | Free Tier | Must Show Map? |
|---|---|---|
| **LocationIQ** (recommended) | 5K req/day | No |
| **Geoapify** | 3K credits/day | No |
| **MapTiler** | 100K req/month (non-commercial) | No |
| **Nominatim** (OSM) | 1 req/sec, no autocomplete | No |
| **Google Places** | $200/month credit | Yes -- must show Google Maps |
| **Mapbox** | 100K req/month | Yes -- must show Mapbox map |

LocationIQ is recommended: most generous free tier, works without a map display, and has an autocomplete endpoint.

See: `research_web_app_apis/geocoding_comparison.md`

**Your answer:**

---

## 6. Camera Sensor Size Detection

**Question:** Do you want to invest in the three-tier automatic sensor detection, or start with manual entry only?

| Approach | Coverage | Effort |
|---|---|---|
| **Three-tier** (recommended) | ~95% auto-detection | ~1 day |
| **EXIF crop factor only** | ~80% auto-detection | ~2 hours |
| **Manual entry only** | 0% auto-detection | ~30 min |

The three-tier approach (EXIF crop factor -> Lensfun JSON lookup -> manual fallback) covers the vast majority of cameras automatically. But it takes more development time.

See: `research_web_app_apis/sensor_size_approaches.md`

**Your answer:**

---

## 7. HEIC Handling Strategy

**Question:** Where should HEIC conversion happen?

| Approach | Pros | Cons |
|---|---|---|
| **Client-side** (heic2any in browser) | No server load, works before upload | 200 KB WASM bundle, slower on old phones |
| **Server-side** (pillow-heif) | Simpler frontend, more reliable | Upload raw HEIC (larger), server does more work |
| **Both** (recommended) | Client converts for preview, server handles processing | More code, but best UX |

The recommended approach: extract EXIF client-side (exifr handles HEIC directly, no conversion needed), convert to JPEG client-side for preview only, then send the original file to the server where pillow-heif processes it.

See: `research_image_handling/exif_extraction.md`

**Your answer:**

---

## 8. Animation Approach

**Question:** Which animation approach for the analemma visualization?

| Approach | Complexity | Quality |
|---|---|---|
| **SVG path + Svelte `draw`** (recommended) | Low (if using Svelte) | High -- smooth, interactive, resolution-independent |
| **SVG path + CSS/GSAP** | Medium | High -- same visual result, more manual code |
| **Canvas** | Higher | High -- better for complex effects (glow/particles) |
| **Static image only** | Minimal | No animation |

If you choose Svelte, the SVG path animation is nearly free -- it's a built-in feature. The backend needs a new JSON endpoint that returns the analemma curve as coordinate data instead of a rendered PNG.

See: `research_image_handling/analemma_animation.md`

**Your answer:**

---

## 9. Backend Engine Changes

**Question:** Should the backend expose both endpoints (JSON data + rendered PNG)?

| Option | What It Means |
|---|---|
| **JSON only** | Frontend renders everything (SVG overlay, animation). Download button triggers a separate "render PNG" request. |
| **Both JSON + PNG** (recommended) | JSON endpoint for animation. PNG endpoint for download. Reuses existing overlay_analemma() code. |
| **PNG only** | No animation. Frontend just displays the returned image. Simplest but loses the key feature. |

The "both" approach gives you animated visualization on the page AND a downloadable static image. The JSON endpoint is new code; the PNG endpoint wraps the existing engine.

See: `research_image_handling/analemma_animation.md` (Backend Changes section)

**Your answer:**

---

## 10. Image Format Support

**Question:** Which image formats should V1 support?

| Tier | Formats | Effort |
|---|---|---|
| **Day 1** (recommended minimum) | JPEG, HEIC, PNG | Add `pillow-heif` to backend deps, `heic2any` to frontend |
| **Day 1 extended** | + WebP | Pillow handles natively, just add to accept list |
| **V2** | + TIFF, DNG | Niche formats, large files, low priority |
| **Out of scope** | RAW (.cr2, .nef, .arw) | Requires rawpy/LibRaw, not worth it |

See: `research_image_handling/image_format_compatibility.md`

**Your answer:**

---

## 11. Sample Images for the Gallery

**Question:** Which sample images should appear on the website?

The images with clear Creative Commons licenses from Wikimedia:

| Image | License | Safe for Web? |
|---|---|---|
| brofjorden | CC BY-SA 4.0 | Yes -- overlay output must also be CC BY-SA 4.0 |
| cold_canada | CC BY 2.0 | Yes -- just need attribution |
| hongkong | CC BY-SA 4.0 | Yes -- overlay output must also be CC BY-SA 4.0 |
| hunan | CC0 1.0 | Yes -- no restrictions |
| sharjah_sands | CC BY 4.0 | Yes -- just need attribution |
| russia_meadow | CC BY-SA 4.0 | Yes -- overlay output must also be CC BY-SA 4.0 |

The personal photos (nigeria, raghav, raghav2, raghav6, robert_hawaii) should NOT be included on the public website without explicit permission.

**Sub-questions:**
- Do you want all 6 CC-licensed images in the gallery, or a curated subset?
- For the personal photos: do you have permission to use your own and Robert's on the website?

See: `research_licensing/attribution_guide.md`, `research_licensing/web_display_and_uploads.md`

**Your answer:**

---

## 12. Licensing Setup

**Question:** Confirm the licensing approach.

The research recommends:
- **Code**: MIT license (in `LICENSE` file at repo root)
- **CC images**: Each retains its own license, documented in `NOTICE` file
- **Overlay outputs from CC BY-SA images**: labeled CC BY-SA 4.0 on the website
- **User-uploaded images**: not stored, not licensed by us, simple ToS disclaimer
- **Personal photos**: remove from public repo or get explicit permission

Are you comfortable with this approach? Anything you want to change?

See: `research_licensing/sharealike_analysis.md`, `research_licensing/repo_structure.md`

**Your answer:**

---

## 13. Frontend Layout

**Question:** Which layout concept do you prefer?

| Concept | Description | Best For |
|---|---|---|
| **A: Single Column** | Vertical flow, one step at a time | Mobile-first, simplest |
| **B: Split Panel** (recommended) | Image left, controls right; collapses on mobile | Best desktop experience |
| **C: Wizard Steps** | Full-screen cards, step by step | Guided experience, more clicks |

See: `research_web_deployment/frontend_design.md`

**Your answer:**

---

## 14. EXIF Auto-Fill Scope

**Question:** How much should we auto-fill from EXIF data?

| Level | What's Auto-Filled | User Effort |
|---|---|---|
| **Full** (recommended) | Datetime, GPS, focal length, camera model, sensor size (via crop factor/lookup) | Minimal -- just verify and click Generate |
| **Partial** | Datetime, GPS, focal length, camera model only. Sensor size manual. | User needs to look up sensor size |
| **None** | All fields manual | Maximum user effort |

The "Full" level is what makes the app feel polished. If EXIF is rich (iPhone photos), the user might not need to type anything.

**Your answer:**

---

## 15. Project Name / Branding

**Question:** What should the web app be called?

The engine is "Analemma Engine" or "Analemma Vision Engine." For the web app, you might want something catchier:

- "Analemma" (simple)
- "Analemma Vision"
- "Solar Trace"
- "Figure Eight"
- Something else?

This affects the domain, the page title, the README, etc.

**Your answer:**

---

## Summary

Once you answer these 15 questions, the research files will be updated with your decisions, and a condensed set of "setup instruction" files will be generated. Those files, along with your answers, are what the PLAN agent will use to build the comprehensive implementation plan.
