# Geocoding / Place Autocomplete API Comparison

We need an autocomplete-style geocoding API: the user types a location name (city, landmark, address) and we return latitude/longitude. The key use case is city-level -- not street-address-level -- since analemma calculations only need approximate GPS coordinates.

## Comparison Table

| Service | Free Tier | Autocomplete Support | Accuracy | Frontend Widget | ToS / Attribution | Latency | Worldwide |
|---|---|---|---|---|---|---|---|
| **Google Places Autocomplete** | 10K requests/month ($200 credit) | Yes, native. Session tokens reduce cost. | Excellent. Best-in-class POI + address data. | Official JS widget, React wrapper available. | Must display Google logo. Results must show on Google Map or link to Google Maps. | ~100-200ms | Yes |
| **Mapbox Search Box** | 500 sessions/month (Search Box) or 100K req/month (Temporary Geocoding) | Yes. Each keystroke = 1 request unless using sessions. `types=place` for cities. | Very good. Strong in US/Europe, decent globally. | `@mapbox/search-js-react`, vanilla JS available. | Must display results on a Mapbox map. "Temporary Geocoding" can't store results. | ~50-150ms | Yes |
| **Nominatim (OSM)** | Unlimited (self-hosted) or 1 req/sec (public API) | No built-in autocomplete-as-you-type. Designed for form-submit search. | Good for cities/countries. Inconsistent for small addresses in developing countries. | None official. DIY with debounced fetch. | ODbL license. Must credit OSM. | ~200-500ms (public API) | Yes (OSM coverage) |
| **Photon (komoot)** | Unlimited (self-hosted). Public demo at photon.komoot.io (no SLA). | Yes, search-as-you-type with typo tolerance. | Same as Nominatim (uses OSM data via Nominatim import). | None. REST API only. | Apache 2.0. Credit OSM. | ~50-200ms (self-hosted) | Yes (OSM coverage) |
| **Geoapify** | 3,000 credits/day (~90K/month). 5 req/sec. | Yes, dedicated autocomplete endpoint. | Good. Uses OSM + other open datasets. | JS library available. | Free tier: must credit Geoapify. Can store results. | ~50-150ms (claimed) | Yes |
| **LocationIQ** | 5,000 req/day (~150K/month). 2 req/sec. | Yes, autocomplete endpoint. | Good. OSM-based. | JS autocomplete widget. | Must credit LocationIQ/OSM. Can cache results. | <100ms (claimed) | Yes |
| **MapTiler Geocoding** | 100K req/month (non-commercial). | Yes, built-in autocomplete. | Good. Custom-processed OSM data. 95% queries <15ms claimed. | `@maptiler/geocoding-control` for React, vanilla JS. | Free tier: non-commercial only. Must credit MapTiler. | <15ms (95th percentile, claimed) | Yes |
| **Pelias** (self-hosted) | Unlimited (self-hosted, MIT license). Commercial API via Geocode Earth. | Yes, autocomplete endpoint. | Excellent for its data sources (OSM + OpenAddresses + Who's on First + Geonames). | None official. REST API. | MIT license. Credit data sources (OSM, etc). | Depends on hardware | Yes |
| **Algolia Places** | **DEAD.** Sunset May 31, 2022. | N/A | N/A | N/A | N/A | N/A | N/A |
| **PlaceKit** | 10K req/month free. | Yes, autocomplete SDK (`@placekit/client-js`). | Decent. Positioned as Algolia Places successor. | JS SDK with drop-in autocomplete. | Must credit PlaceKit on free tier. | Not benchmarked | Yes |

## Detailed Notes per Service

### Google Places Autocomplete

The gold standard for user-facing autocomplete. Exceptionally good data quality -- handles typos, abbreviations, alternate names, and POIs.

**Pricing**: Google gives a $200/month free credit which covers ~10,000 Autocomplete requests or ~40,000 if you use session tokens (session token bundles multiple keystrokes into one "session" billed at $0.017). After the free credit, it's $2.83 per 1,000 requests (no session) or $17 per 1,000 sessions.

**Key restriction**: Results must be displayed on a Google Map or link to a Google Maps page. Using the data without showing a map violates the ToS. For our use case (just extracting lat/long, no map), this is a problem unless we add a small Google Map to the UI.

**Filter**: `types=(cities)` restricts results to cities only, which is exactly what we need.

### Mapbox Search Box / Geocoding

Two products with confusing overlap:
- **Search Box** (newer): Session-based pricing, 500 free sessions/month. Better for autocomplete UX.
- **Temporary Geocoding** (older): 100,000 free requests/month. Results can't be stored.

**Key restriction**: Like Google, Mapbox requires results to be displayed on a Mapbox map. The "Temporary Geocoding" product explicitly prohibits storing or caching results without a map. This is another ToS problem for our use case.

**Filter**: `types=place` restricts to cities/towns. Rate limit: 1,000 req/min.

### Nominatim (OSM Direct)

The canonical OSM geocoder. Free to self-host, and there's a public instance at nominatim.openstreetmap.org with a strict 1 request/second rate limit and no autocomplete. 

Not designed for typeahead/autocomplete. You'd need to debounce heavily (300-500ms) and it still feels sluggish compared to purpose-built autocomplete APIs. Best used as a backend geocoding tool (user submits a form, you geocode it).

**Filter**: `featuretype=city` limits to city-level results.

**Hosting**: Self-hosting a full planet import requires ~1.5TB SSD + 64GB RAM. Overkill for our use case.

### Photon (komoot)

Open-source Java geocoder that imports Nominatim data and adds search-as-you-type with typo tolerance and multilingual support. It's what Nominatim should have been for autocomplete.

**Catch**: Self-hosting requires ~95GB storage for planet data and 64GB RAM recommended. The public demo at photon.komoot.io has no SLA, no rate limit guarantees, and could go down anytime.

**License**: Apache 2.0 (code), ODbL (data from OSM).

Good for a self-hosted production deployment. Too heavy for a hobby project's V1.

### Geoapify

German company, GDPR-compliant. Generous free tier (3,000 credits/day, where autocomplete = 1 credit). Dedicated autocomplete endpoint with good response structure.

**Advantage**: Explicitly allows storing/caching results. No map display requirement. This is a big deal compared to Google/Mapbox.

**Paid plans**: Start at EUR 59/month for 10K credits/day.

### LocationIQ

Most generous free tier of the commercial options: 5,000 requests/day (~150K/month). Uses OSM data. Has a dedicated autocomplete endpoint.

**Advantage**: Can cache results. Simple attribution (credit LocationIQ and OSM). No map display requirement. Response times <100ms.

**Paid plans**: Start at $45/month for 10K req/day, 10 req/sec.

**Downside**: OSM data quality -- same limitations as Nominatim for obscure locations. But for city-level geocoding, this is fine.

### MapTiler Geocoding

Impressively fast (claimed 95% of queries under 15ms). Free tier is 100K requests/month but limited to non-commercial use.

Has a nice drop-in geocoding control (`@maptiler/geocoding-control`) with React and vanilla JS versions that handle the autocomplete UI.

**Downside**: Free tier is non-commercial only. If the web app ever becomes anything beyond a personal project, you'd need the Flex plan at $25/month for 500K requests.

### Pelias (Self-Hosted)

The most powerful open-source option. MIT-licensed. Uses Elasticsearch under the hood with data from OSM, OpenAddresses, Who's on First, and Geonames. Run by the Linux Foundation (originally from Mapzen).

Has a proper autocomplete endpoint. Data quality is excellent when all sources are imported.

**Catch**: Infrastructure requirements are substantial. Docker-based setup, needs Elasticsearch, multiple importers. A planet-scale build needs serious hardware. The commercial API is at geocode.earth (pricing not publicly listed, trial available).

3,500 GitHub stars, active maintenance.

### Algolia Places

Dead. Algolia announced the sunset in May 2023, with the service ending May 31, 2022 (the blog post was published after the fact). They recommended PlaceKit, Mapbox, Google Places, or Geocode Earth as alternatives.

### PlaceKit

Built as a direct Algolia Places replacement by a Paris-based team. 10K free requests/month. Clean API with a JS SDK that provides a drop-in autocomplete component.

**Pricing**: Pay-per-request after 10K free. $0.003/request for 0-50K, scaling down to $0.0015/request at 500K-1M.

Relatively new. Less battle-tested than the bigger players.

## Summary: What Matters for This Project

Our use case is simple: city-level geocoding with autocomplete, low volume, worldwide coverage, no map display. The disqualifying factors for some APIs:

- **Google Places**: ToS requires map display. We'd need to add a Google Map or violate ToS.
- **Mapbox**: Same map display requirement. Temporary Geocoding can't store results.
- **Algolia Places**: Dead.
- **Nominatim**: No autocomplete. Sluggish for typeahead.
- **Photon / Pelias**: Too heavy to self-host for a hobby project.

The strongest candidates for V1 are **LocationIQ**, **Geoapify**, **MapTiler**, and **PlaceKit** -- all have autocomplete, generous free tiers, no map display requirement, and worldwide coverage.
