# Deployment Research: Overview

Research conducted March 2026 for deploying the Analemma Vision Engine web application.

## The Problem

We need to deploy a two-part web application:

1. **Frontend** -- Svelte or Vue SPA. Static files, probably 1-5 MB after build. Needs CDN delivery, custom domain, HTTPS.
2. **Backend** -- FastAPI Python API. Heavy scientific dependencies (astropy, scipy, numpy, Pillow, timezonefinder). Docker image ~800MB-1GB. CPU-bound processing (3-10 seconds per request). No database, no auth.

Key constraints:
- Educational/portfolio project -- low traffic, low budget
- Developer has the **GitHub Student Developer Pack**
- Must support Docker for the backend (the dependency stack is too large for buildpacks)
- Custom domain desired (free domain available from student pack)
- Image upload + processing workflow (several seconds per request)

## Student Pack Credits Summary

| Provider | Offer | Duration | Effective value |
|----------|-------|----------|-----------------|
| Heroku | $13/month credit | 24 months | $312 total |
| DigitalOcean | $200 platform credit | 1 year | $200 total |
| Microsoft Azure | $100 credit + 25 free services | 1 year | ~$100+ |
| Namecheap | Free .me domain + 1 SSL cert | 1 year | ~$15 |
| Name.com | Free domain (.live, .studio, .software, .app, .dev) | 1 year | ~$15-35 |
| Appwrite | Education plan (10 projects, Pro-equivalent) | While student | ~$160/month value |

## Research Files

- [overview.md](overview.md) -- this file
- [frontend_hosting.md](frontend_hosting.md) -- comparison of frontend/static hosting options
- [backend_hosting.md](backend_hosting.md) -- comparison of backend/API hosting options
- [combo_hosting.md](combo_hosting.md) -- platforms that host both frontend and backend
- [ci_cd_and_repo_structure.md](ci_cd_and_repo_structure.md) -- GitHub Actions, monorepo vs multi-repo, custom domains
- [recommendations.md](recommendations.md) -- top 3-4 deployment configurations with cost breakdown
