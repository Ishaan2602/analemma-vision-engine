# License Details -- CC BY 2.0, CC BY 4.0, CC BY-SA 4.0, CC0 1.0

Per-license breakdown of what each license requires and allows, applied to this project's specific use case (including images in a repo, displaying them on a website, and overlaying computed curves on them).

---

## CC0 1.0 Universal (Public Domain Dedication)

**Used by:** hunan (Huangdan2060)

CC0 isn't a license -- it's a public domain dedication. The creator waives all rights to the maximum extent allowed by law.

**Requirements:** None. Zero obligations.

**Can you:**
- Include it in the repo? Yes
- Display it on the website? Yes
- Overlay it with an analemma? Yes
- License the overlay under MIT? Yes, or any license, or no license
- Use it commercially? Yes
- Modify it without noting modifications? Yes

**Best practice (not required):**
CC recommends citing the source anyway, as a professional courtesy:
> "Landscape with Rising Sun in Dongkou County" by Huangdan2060. Public domain (CC0 1.0).
> Source: https://commons.wikimedia.org/wiki/File:Landscape_with_Rising_Sun_in_Dongkou_County.jpg

---

## CC BY 2.0 Generic

**Used by:** cold_canada (Emmanuel Huybrechts)

The oldest license version in the project. CC BY 2.0 predates the 4.0 international suite, but the core requirements are similar.

**Requirements:**
1. **Attribution** -- credit the author, provide the title, link to the license
2. **Indicate changes** -- if you created an adaptation, note it (in 2.0, this is specifically required for adaptations; in 4.0 it's required for any modification)

**Differences from CC BY 4.0:**
- 2.0 licenses are jurisdiction-specific (this one is "Generic" / unported)
- 2.0 requires the title to be included; 4.0 makes title optional
- 2.0's adaptation indicator only applies if you created an adaptation by contributing new creative material; 4.0 requires indicating any modification
- 2.0 does not have the automatic 30-day cure period for violations that 4.0 introduced
- 2.0 does not explicitly license sui generis database rights

**No ShareAlike.** The overlay image can be under any license.

**No NonCommercial.** Commercial use is fine.

**Can you:**
- Include it in the repo? Yes, with attribution
- Display it on the website? Yes, with attribution
- Overlay it with an analemma? Yes -- it's an adaptation, so note the modification and attribute
- License the overlay under any terms? Yes
- Use it commercially? Yes

---

## CC BY 4.0 International

**Used by:** sharjah_sands (Aleksandr Serebrennikov)

The current-generation attribution-only license. Most permissive of the standard CC licenses (excluding CC0).

**Requirements:**
1. **Attribution** (TASL: Title, Author, Source, License)
   - Identification of the creator
   - Copyright notice (if provided)
   - License notice (link to CC BY 4.0)
   - Disclaimer of warranties notice
   - URI/hyperlink to the original work (if reasonably practicable)
2. **Indicate modifications** -- if you modified the work, say so
3. **Retain indication of previous modifications** (if any)

**No ShareAlike.** The overlay image can be under any license.

**No NonCommercial.** Commercial use is fine.

**4.0-specific features:**
- International (not jurisdiction-specific)
- 30-day automatic cure period for license violations
- Sui generis database rights included
- Format shifting is explicitly an allowed "technical modification," not an adaptation

**Can you:**
- Include it in the repo? Yes, with attribution
- Display it on the website? Yes, with attribution
- Overlay it with an analemma? Yes -- note the modification and attribute
- License the overlay under any terms? Yes
- Use it commercially? Yes

---

## CC BY-SA 4.0 International

**Used by:** brofjorden (W.carter), hongkong (Kailanchoi), russia_meadow (Roman Eisele)

Same as CC BY 4.0, plus the ShareAlike condition.

**Requirements:**
1. **Everything from CC BY 4.0** (attribution, indicate modifications, etc.)
2. **ShareAlike** -- if you share Adapted Material (derivatives), you must use CC BY-SA 4.0 (or a compatible license) as your adapter's license

**What counts as Adapted Material:**
Per the legal code: material "derived from or based upon the Licensed Material and in which the Licensed Material is translated, altered, arranged, transformed, or otherwise modified in a manner requiring permission under the Copyright and Similar Rights."

The analemma overlay almost certainly qualifies as Adapted Material (see [sharealike_analysis.md](sharealike_analysis.md)).

**ShareAlike scope:**
- Applies to the **output image** (photo + overlay), not to your code
- Applies **per-image** -- a CC BY-SA input means a CC BY-SA output; doesn't affect other images
- Does NOT require you to share the output publicly -- ShareAlike only kicks in "if you Share"
- The **repository as a collection** can be MIT-licensed; ShareAlike doesn't apply to collections

**Compatible licenses for ShareAlike:**
CC maintains a list at https://creativecommons.org/compatiblelicenses. Currently, GPLv3 is the only approved BY-SA Compatible License. But since we're dealing with images (not code), CC BY-SA 4.0 is the natural choice for the adapter's license.

**Can you:**
- Include it in the repo? Yes, with attribution
- Display it on the website? Yes, with attribution
- Overlay it with an analemma? Yes, but the output must be CC BY-SA 4.0
- License the overlay under MIT? No -- the overlay image must be CC BY-SA 4.0
- Use it commercially? Yes (BY-SA allows commercial use)
- MIT-license the code that produces the overlay? Yes -- code is separate from output

---

## Summary table

| License | Attribution | Note modifications | ShareAlike on output | Commercial OK |
|---------|:-----------:|:------------------:|:--------------------:|:-------------:|
| CC0 1.0 | No (recommended) | No | No | Yes |
| CC BY 2.0 | Yes | Yes (for adaptations) | No | Yes |
| CC BY 4.0 | Yes | Yes (any modification) | No | Yes |
| CC BY-SA 4.0 | Yes | Yes (any modification) | Yes | Yes |
