# Web App API Research: Overview

Research conducted for two integration points needed by the Analemma web application:

1. **Geocoding / Place Autocomplete** -- users type a city or location name, we need lat/long coordinates
2. **Camera Sensor Size Lookup** -- users input their camera model (or we auto-detect it), we need sensor_width_mm and sensor_height_mm

Both capabilities currently live in the metadata.txt file that users fill out manually. The web app needs to make this frictionless.

## Context

The Analemma Vision Engine accepts GPS coordinates and camera sensor dimensions as inputs. In the CLI/notebook workflow, users type these into a metadata file by hand. For a web app, we want:

- A location autocomplete box where users type "Hong Kong" or "Sharjah" and get coordinates
- Automatic camera detection from the uploaded photo's EXIF data, with sensor size auto-populated

The backend is FastAPI (see `research_backend_framework/`). The frontend is likely Svelte/SvelteKit or Vue 3 (see `research_frontend_frameworks/`). Both of these choices affect which geocoding widgets and EXIF libraries make sense.

## Research Files

| File | Contents |
|---|---|
| [geocoding_comparison.md](geocoding_comparison.md) | Full comparison of 10 geocoding/autocomplete APIs across 7 criteria |
| [sensor_size_approaches.md](sensor_size_approaches.md) | 7 approaches for camera sensor size lookup, with coverage and feasibility analysis |
| [recommendations.md](recommendations.md) | Final recommendations for V1 implementation of both features |

## Key Constraints

- **Budget**: Free tier or very cheap. This is a hobby/portfolio project, not a SaaS business.
- **Volume**: Low. Maybe a few hundred requests per day at peak.
- **Worldwide coverage**: Users photograph from everywhere -- UAE, Nigeria, Russia, Hong Kong, Hawaii.
- **No map display required**: We just need coordinates, not a rendered map. This matters because some APIs (Mapbox, Google) have ToS clauses requiring map display.
- **Simplicity**: One developer. Minimal integration complexity wins.
