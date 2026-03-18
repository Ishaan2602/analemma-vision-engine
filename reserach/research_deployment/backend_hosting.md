# Backend Hosting Comparison

The backend is a FastAPI Python API with heavy scientific dependencies (astropy ~100MB, scipy ~70MB, numpy ~30MB, Pillow ~20MB, timezonefinder ~40MB). The Docker image is ~800MB-1GB. Processing is CPU-bound (3-10 seconds per request). No database needed.

## Summary Table

| Feature | Render (Free) | Render (Starter $7) | Heroku (Student $13/mo credit) | DigitalOcean App Platform ($200 credit) | Fly.io (Pay-as-you-go) | Railway (Hobby $5/mo) |
|---------|--------------|--------------------|---------------------------------|-----------------------------------------|------------------------|----------------------|
| **Monthly cost** | $0 | $7/mo | $0 (covered by credit) | $0 (covered by credit) | ~$5-11/mo | ~$5/mo |
| **Docker support** | Yes | Yes | Yes (container registry) | Yes | Yes (native) | Yes |
| **RAM** | 512 MB | 512 MB | 512 MB (Eco/Basic) | 512 MB-2 GB | 256 MB-2 GB+ | Up to 0.5 GB (free), 8 GB (hobby) |
| **CPU** | 0.1 vCPU | 0.5 vCPU | Shared 1x | 1 vCPU shared | 1 shared | Up to 1 vCPU (free) |
| **Cold start** | ~60s (spins down after 15 min) | No spin-down | ~30s (Eco sleeps after 30 min) | No spin-down on paid | Configurable auto-stop | No auto-sleep |
| **Custom domain** | Yes | Yes | Yes | Yes | Yes | No (free plan), 2 (hobby) |
| **HTTPS** | Auto | Auto | Auto | Auto | Auto (Let's Encrypt, $0.10/mo first 10 free) | Auto |
| **Bandwidth** | 100 GB/mo included | 100 GB/mo included | Included | 50-250 GiB depending on plan | Egress: $0.02/GB NA/EU | Egress: $0.05/GB |
| **CI/CD from GitHub** | Auto-deploy on push | Auto-deploy on push | Auto-deploy via GitHub integration | Auto-deploy from GitHub/GitLab | Via `fly deploy` or GitHub Actions | Auto-deploy on push |
| **Build pipeline** | Dockerfile on platform | Dockerfile on platform | Dockerfile or heroku.yml | Dockerfile | Dockerfile (local or remote builder) | Dockerfile or Nixpacks |

## Detailed Analysis

### Render -- Free Tier

**The deal:** Free web service with 512 MB RAM, 0.1 vCPU. Spins down after 15 minutes of inactivity. 750 free instance hours/month (enough for one service running continuously when active).

**Docker:** Full Dockerfile support. Builds run on Render's infrastructure.

**The problem for us:** 512 MB RAM with 0.1 vCPU is almost certainly not enough. Importing astropy + scipy + numpy alone will consume 300-400 MB of RAM. Add the actual computation (loading a JPL ephemeris, image processing) and you'll hit the memory limit on first request. The 0.1 vCPU will make the ~5 second computation take 50+ seconds.

**Cold start:** Service spins down after 15 minutes idle. Spin-up takes ~60 seconds (pulling image, starting Python, loading modules). For a demo project this is painful -- every time someone visits your portfolio, they wait a full minute.

**Verdict:** Only suitable for a proof-of-concept demo where you're okay with very slow responses. Not a good experience for a portfolio showcase.

### Render -- Starter ($7/month) and Standard ($25/month)

**Starter ($7/mo):** 512 MB RAM, 0.5 vCPU. No spin-down. This is much better CPU but the same RAM constraint. Our dependency stack will fit, but barely -- any request with a large image might OOM.

**Standard ($25/mo):** 2 GB RAM, 1 vCPU. No spin-down. This is the sweet spot for our workload. Enough RAM for the full stack plus image processing, and a full vCPU for reasonable computation time.

**Docker:** Supported. Auto-deploys on git push. Excellent GitHub integration.

**Build pipeline:** 500 minutes/month on the Hobby workspace plan (free). A Docker build from cache might take 2-5 minutes. That's 100-250 deploys/month -- plenty.

**Verdict:** Standard ($25/mo) is the right Render tier for this project. However, that eats through any free budget fast.

### Heroku with Student Credit ($13/month for 24 months)

**The deal:** $13/month credit applied to your Heroku account. That covers the Eco ($5/mo pool) or Basic ($7/mo per dyno) tiers, but not much more.

**Dyno sizes relevant to us:**

| Dyno | RAM | CPU | Price | Fits our stack? |
|------|-----|-----|-------|-----------------|
| Eco | 512 MB | Shared 1x | $5/mo (pool) | Barely. Sleeps after 30 min. |
| Basic | 512 MB | Shared 1x | $7/mo | Barely. No sleep. |
| Standard-1X | 512 MB | Shared 1x | $25/mo | Same RAM, but autoscale. Over budget. |
| Standard-2X | 1 GB | Shared 2x | $50/mo | Better, but $50 - $13 = $37/mo out of pocket. |

**Docker support:** Yes, via `heroku.yml` or the container registry (`heroku container:push`). This bypasses the normal buildpack (important, since the slug size limit of 500 MB would be a problem for our deps).

**The problem:** With $13/month credit, you can afford a Basic dyno ($7/mo) -- leaving $6/mo unused credit. But the Basic dyno only has 512 MB RAM with shared CPU. Same memory concern as Render Free: astropy + scipy + numpy will push you close to the limit, and image processing on top of that will be tight.

The 500 MB slug size limit doesn't apply to Docker deployments, which is good. But the 512 MB RAM does apply.

**Cold start (Eco):** Eco dynos sleep after 30 minutes of inactivity. Cold boot from Docker is slow with our dep stack (30-60 seconds). Basic dynos don't sleep.

**Verdict:** Heroku's student credit gets you a Basic dyno that stays awake but is memory-constrained. For $13/mo you could instead get a bigger machine elsewhere. The credit is most useful as "free hosting that works for 24 months" if 512 MB is enough.

### DigitalOcean App Platform (with $200 Student Credit)

**The deal:** $200 in platform credit for 1 year. You can use it on any DO product: App Platform, Droplets, Kubernetes, etc.

**App Platform container pricing:**

| Tier | vCPU | RAM | Bandwidth | Price | Months covered by $200 |
|------|------|-----|-----------|-------|----------------------|
| Shared Fixed | 1 | 512 MiB | 50 GiB | $5/mo | 40 (but credit expires in 12) |
| Shared Fixed | 1 | 1 GiB | 100 GiB | $10/mo | 20 |
| Shared | 1 | 2 GiB | 200 GiB | $25/mo | 8 |
| Shared | 2 | 4 GiB | 250 GiB | $50/mo | 4 |

**Docker support:** Full Dockerfile support. Deploy from GitHub or a container registry.

**Alternative: Droplet (VPS):** Instead of App Platform, you could use a Droplet (raw VM):
- $6/mo: 1 vCPU, 1 GB RAM, 25 GB SSD, 1 TB bandwidth (~33 months of credit)
- $12/mo: 1 vCPU, 2 GB RAM, 50 GB SSD, 2 TB bandwidth (~16 months)
- $18/mo: 2 vCPU, 2 GB RAM, 60 GB SSD, 3 TB bandwidth (~11 months)
- $24/mo: 2 vCPU, 4 GB RAM, 80 GB SSD, 4 TB bandwidth (~8 months)

A Droplet gives you more control but requires manual server setup (install Docker, set up nginx, SSL certs via certbot, etc.). App Platform handles all that.

**No cold start:** Paid containers on App Platform don't spin down. Droplets are always running.

**Verdict:** The $200 credit makes DO the most cost-effective option. You get 8-12+ months of hosting with enough RAM for the full stack. App Platform at $10/mo (1 vCPU, 1 GiB RAM) is the sweet spot -- 1 GiB is tight but workable if you trim deps, and you get 20 months of coverage (capped at 12 by credit expiration). At $25/mo (2 GiB RAM) you get 8 months -- comfortable RAM but the credit runs out faster. A $12/mo Droplet with 2 GB RAM is even better value if you're willing to do manual server setup.

### Fly.io (Pay-as-you-go)

**The deal:** No free tier for new accounts (legacy free allowances were discontinued). Pure pay-as-you-go billed per second of machine uptime.

**Pricing for our workload:**

| Machine | RAM | Monthly (running 24/7) |
|---------|-----|----------------------|
| shared-cpu-1x, 512 MB | 512 MB | $3.19 |
| shared-cpu-1x, 1 GB | 1 GB | $5.70 |
| shared-cpu-1x, 2 GB | 2 GB | $10.70 |
| shared-cpu-2x, 2 GB | 2 GB | $11.39 |

Plus: shared IPv4 (free), SSL certs (first 10 free), egress (~$0.02/GB in NA/EU).

**Docker support:** Native and excellent. Fly deploys directly from Dockerfiles via `fly deploy`. One of the best Docker-native platforms.

**Auto-stop/auto-start:** Fly Machines can be configured to auto-stop when idle and auto-start on incoming requests. This means you only pay when the machine is running. If your app gets a few requests per day, your bill could drop to $1-2/month instead of the full 24/7 price.

**Cold start with auto-stop:** Fly Machines start faster than Render/Heroku because they're actual microVMs, not containers being rebuilt. But loading our Python stack will still take 15-30 seconds on cold start.

**Regions:** Deploy close to users in 30+ regions worldwide.

**Verdict:** Fly.io is well-priced and has the best Docker experience. A shared-cpu-1x with 1-2 GB RAM at $5.70-$10.70/month is competitive. The auto-stop feature can reduce costs if traffic is sporadic. But there's no student discount and no free tier, so this is out-of-pocket cost from day one.

### Railway (Hobby Plan -- $5/mo)

**The deal:** $5/month gives you $5 of usage credits. Usage-based billing per second of CPU and RAM. After the credits, you pay for excess usage.

**Pricing math:**
- Memory: $0.000386/GB/hour = ~$2.78/GB/month
- CPU: $0.000772/vCPU/hour = ~$5.56/vCPU/month
- Egress: $0.05/GB

A service using 1 vCPU and 1 GB RAM continuously would cost ~$8.34/month. So the $5 credit covers about 60% of the bill; you'd pay ~$3.34 extra.

**Docker support:** Dockerfile or Nixpacks (auto-detected). Railway is very Docker-friendly.

**Resource limits (Hobby):** Up to 48 vCPU and 48 GB RAM per service (you pay for what you use). Up to 5 GB storage. 7-day log history.

**No cold start:** Railway doesn't auto-sleep services by default.

**Custom domains:** 2 custom domains on Hobby plan.

**Cons:**
- Free plan (Trial) is limited: 0.5 GB RAM, 1 vCPU after trial ends, and $1/month after the 30-day free trial. No custom domains on free plan post-trial.
- The Hobby plan at $5/mo is effectively $8-10/mo for our workload.
- Railway's durability and long-term pricing stability are less proven than Render or DO.

**Verdict:** Railway is a nice platform with excellent DX, but it's not the cheapest for an always-on service with our resource needs. Similar cost to Fly.io without the student discount advantage.

## The RAM Problem

Our stack requires at minimum ~500 MB just to import the core libraries. With the JPL ephemeris loaded and an image in memory during processing, peak usage will hit 700-900 MB. Here's the breakdown:

| Component | Estimated RAM | Notes |
|-----------|--------------|-------|
| Python runtime | ~50 MB | Base interpreter |
| numpy + scipy | ~100 MB | Imported modules |
| astropy + IERS data | ~150 MB | Coordinate frames, units |
| JPL DE440 ephemeris | ~100 MB | Loaded into memory on first calc |
| Pillow + loaded image | ~50-100 MB | Depends on input image size |
| FastAPI + Uvicorn | ~30 MB | Lightweight |
| **Total baseline** | **~480-530 MB** | |
| **Peak during processing** | **~700-900 MB** | |

**512 MB tiers will struggle.** They might work for small images if you're lucky, but it's fragile. **1 GB is the minimum comfortable tier. 2 GB gives headroom for larger images and multiple workers.**

## Backend Recommendation

**Primary: DigitalOcean App Platform ($10-25/month, covered by $200 student credit)**

The student credit gives you 8-20 months of free hosting depending on the tier. The $10/month tier (1 vCPU, 1 GiB) is tight but workable with dependency trimming. The $25/month tier (1 vCPU, 2 GiB) is comfortable.

**Runner-up: Fly.io ($5.70-10.70/month, out of pocket)**

Best Docker experience, auto-stop/auto-start can reduce costs. Good for after the DO credit runs out.

**Budget: Heroku Basic ($7/month, covered by $13 student credit)**

Works for 24 months, but 512 MB is tight. Use this if you want longevity over performance.
