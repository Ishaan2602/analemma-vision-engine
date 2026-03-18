# Frontend Framework Comparison -- Overview

Research for the Analemma Engine web frontend. The app is a single-page tool with image upload, metadata forms, location autocomplete, overlay display, animated visualization, and download. No auth, no user accounts.

## Frameworks Evaluated

| Framework | Category | Maturity | GitHub Stars (approx) |
|-----------|----------|----------|-----------------------|
| React + Vite | SPA library | 2013, very mature | ~234k |
| Next.js | React meta-framework (SSR/SSG) | 2016, mature | ~132k |
| Vue 3 + Vite | SPA framework | 2014, mature | ~48k |
| Svelte / SvelteKit | Compiler-based framework | 2016, growing fast | ~82k |
| Vanilla JS + Alpine.js / HTMX | Lightweight / hypermedia | HTMX 2020, Alpine 2020 | HTMX ~48k, Alpine ~29k |
| Astro | Static-first island architecture | 2021, rapidly maturing | ~49k |

## Key Findings at a Glance

**Best overall fit for this project: Svelte/SvelteKit or Vue 3 + Vite.** Both balance simplicity, small bundles, good animation support, and adequate ecosystem. React is the safe default but carries more complexity than this app needs. Next.js is overkill. HTMX/Alpine is under-powered for the animated visualization requirement. Astro is interesting but its content-first philosophy fits blogs better than interactive tools.

See [detailed_comparison.md](detailed_comparison.md) for the full framework-by-framework analysis, and [recommendations.md](recommendations.md) for the final recommendation with reasoning.

## Files in This Research

- [overview.md](overview.md) -- this file
- [detailed_comparison.md](detailed_comparison.md) -- per-framework deep-dive on all evaluation criteria
- [recommendations.md](recommendations.md) -- final ranked recommendations with rationale
- [ecosystem_notes.md](ecosystem_notes.md) -- notes on specific libraries needed (geocoding, EXIF, animation, HEIC)
