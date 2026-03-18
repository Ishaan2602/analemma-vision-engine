# Attribution Guide -- Repo and Website

How to properly attribute each CC-licensed image in the repository (NOTICE file, metadata files) and on the website (image pages, credits section).

---

## The TASL framework

Creative Commons recommends the TASL format for attribution:

- **T**itle -- name of the work
- **A**uthor -- who created it (linked to their profile if available)
- **S**ource -- where you found it (link to the original)
- **L**icense -- which CC license, linked to the license deed

For modifications, also note what you changed.

Source: https://wiki.creativecommons.org/wiki/Best_practices_for_attribution

---

## Attribution templates

### For unmodified images (e.g., in the repo, or as a "before" view on the website)

```
"[Title]" by [Author]. Licensed under [License].
Source: [URL]
```

### For modified images (the analemma overlay outputs)

```
This work is adapted from "[Title]" by [Author], used under [License].
Analemma curve overlay added by Analemma Engine.
[If CC BY-SA:] This adaptation is licensed under CC BY-SA 4.0.
Source: [URL]
```

---

## Per-image attribution text

### brofjorden (CC BY-SA 4.0)

**Unmodified:**
> "Waining sun dog with reflection over Brofjorden" by W.carter. Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
> Source: https://commons.wikimedia.org/wiki/File:Waining_sun_dog_with_reflection_over_Brofjorden.jpg

**Overlaid:**
> This image is adapted from "Waining sun dog with reflection over Brofjorden" by W.carter, used under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Analemma curve overlay added by Analemma Engine. This adaptation is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
> Source: https://commons.wikimedia.org/wiki/File:Waining_sun_dog_with_reflection_over_Brofjorden.jpg

### cold_canada (CC BY 2.0)

**Unmodified:**
> "Cold Sun Landscape" by Emmanuel Huybrechts. Licensed under [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/).
> Source: https://commons.wikimedia.org/wiki/File:Cold_Sun_Landscape_(4698301386).jpg

**Overlaid:**
> This image is adapted from "Cold Sun Landscape" by Emmanuel Huybrechts, used under [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/). Analemma curve overlay added by Analemma Engine.
> Source: https://commons.wikimedia.org/wiki/File:Cold_Sun_Landscape_(4698301386).jpg

### hongkong (CC BY-SA 4.0)

**Unmodified:**
> "Bright light" by Kailanchoi. Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
> Source: https://commons.wikimedia.org/wiki/File:Bright_light.JPG

**Overlaid:**
> This image is adapted from "Bright light" by Kailanchoi, used under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Analemma curve overlay added by Analemma Engine. This adaptation is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
> Source: https://commons.wikimedia.org/wiki/File:Bright_light.JPG

### hunan (CC0 1.0)

**No attribution required. Optional credit:**
> "Landscape with Rising Sun in Dongkou County" by Huangdan2060. Public domain ([CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)).
> Source: https://commons.wikimedia.org/wiki/File:Landscape_with_Rising_Sun_in_Dongkou_County.jpg

### russia_meadow (CC BY-SA 4.0)

**Unmodified:**
> "Ostringen - Tiefenbach - Kreuzbergkapelle" by Roman Eisele. Licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
> Source: https://commons.wikimedia.org/wiki/File:%C3%96stringen_-_Tiefenbach_-_Kreuzbergkapelle_-_Situationsansicht_von_Osten_bei_Sonnenuntergang.jpg

**Overlaid:**
> This image is adapted from "Ostringen - Tiefenbach - Kreuzbergkapelle" by Roman Eisele, used under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Analemma curve overlay added by Analemma Engine. This adaptation is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
> Source: https://commons.wikimedia.org/wiki/File:%C3%96stringen_-_Tiefenbach_-_Kreuzbergkapelle_-_Situationsansicht_von_Osten_bei_Sonnenuntergang.jpg

### sharjah_sands (CC BY 4.0)

**Unmodified:**
> "Sun in the sands" by Aleksandr Serebrennikov. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> Source: https://commons.wikimedia.org/wiki/File:Sun_in_the_sands.jpg

**Overlaid:**
> This image is adapted from "Sun in the sands" by Aleksandr Serebrennikov, used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Analemma curve overlay added by Analemma Engine.
> Source: https://commons.wikimedia.org/wiki/File:Sun_in_the_sands.jpg

---

## Where attribution should appear

### In the repository

1. **NOTICE file** at the repo root -- a single authoritative list of all third-party content and their licenses (see [repo_structure.md](repo_structure.md) for a template)
2. **Individual metadata.txt files** -- already contain license info in comments (good, keep this)
3. **README.md** -- mention that sample images are under CC licenses and point to the NOTICE file

### On the website

Attribution must appear **where the image is displayed**. The CC FAQ says you can satisfy attribution by linking to a page with the info, but the best practice is to show it near the image.

**Option A: Inline attribution (recommended)**
Show attribution text directly below or next to the image on the page where it appears. For a gallery of sample images, this looks like:

```
[Image displayed]
"Bright light" by Kailanchoi | CC BY-SA 4.0 | Source
Analemma overlay added by Analemma Engine
```

**Option B: Credits page (acceptable)**
If inline attribution clutters the UI, link to a `/credits` page from the image caption. The CC FAQ confirms: "you may satisfy the attribution requirement by providing a link to a place where the attribution information may be found."

```
[Image displayed]
Photo credit | CC BY-SA 4.0
(where "Photo credit" links to /credits#brofjorden)
```

**Option C: Image detail page**
If each sample has its own page, put full attribution on that page.

### Recommended approach for the web app

Use **Option A for sample images** (there are only ~6-7 CC images, so it's manageable) and **a separate /credits page** that collects everything in one place for reference. The /credits page should also credit the software's dependencies and any other third-party assets.

---

## Common attribution mistakes to avoid

From the CC wiki's "Common pitfalls":

1. **Don't credit "Wikimedia Commons" or "Creative Commons"** as the author. Credit the actual photographer.
2. **Don't put attribution only in HTML alt text or EXIF metadata.** Most users won't see it. Show it visibly.
3. **Don't omit the license link.** Always link to the specific license deed (e.g., https://creativecommons.org/licenses/by-sa/4.0/).
4. **Don't imply endorsement.** Don't suggest the photographer endorses your project unless they said so.
5. **Don't forget to note modifications.** For overlaid images, always state "Analemma curve overlay added" or similar.
