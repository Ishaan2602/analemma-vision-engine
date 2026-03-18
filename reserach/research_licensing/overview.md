# Licensing Overview -- MIT Code + Creative Commons Images

## The situation

The Analemma Engine is a Python tool that overlays calculated astronomical curves onto sky photographs. The codebase will be MIT-licensed. The repo includes sample sky photos sourced from Wikimedia Commons under various Creative Commons licenses. A web app will let users try these samples and upload their own photos.

The core question: can these coexist in one repo, and what are the obligations?

## Short answer

Yes. Multi-license repos are common and well-established. The key principle: **different licenses apply to different files**. MIT covers the code; each CC license covers only the image it was applied to. There's no conflict as long as the repo clearly marks which license applies to what.

The tricky part is CC BY-SA 4.0's ShareAlike clause and whether the analemma overlay creates a "derivative work" of the photograph. This question has a real answer (see [sharealike_analysis.md](sharealike_analysis.md)), and it affects how you label the output images on the website.

## Inventory of licenses in this project

| Image | License | Key Requirements |
|-------|---------|-----------------|
| brofjorden | CC BY-SA 4.0 | Attribution + ShareAlike on derivatives |
| cold_canada | CC BY 2.0 | Attribution only |
| hongkong | CC BY-SA 4.0 | Attribution + ShareAlike on derivatives |
| hunan | CC0 1.0 | None (public domain) |
| nigeria | User's own photo | No CC license -- need explicit permission or remove |
| raghav, raghav2, raghav6 | User's own photos | No CC license -- need explicit permission or remove |
| robert_hawaii | Friend's photo | No CC license -- need explicit permission or remove |
| russia_meadow | CC BY-SA 4.0 | Attribution + ShareAlike on derivatives |
| sharjah_sands | CC BY 4.0 | Attribution only |

## The four categories

**1. CC0 / Public Domain (hunan)**
No obligations at all. You can do anything with these. CC recommends citing the source as a courtesy, but there's no legal requirement. See [license_details.md](license_details.md).

**2. CC BY (cold_canada, sharjah_sands)**
You must provide attribution (TASL: Title, Author, Source, License). If the overlay is a derivative, you must note the modification. You can license the derivative under any terms, including MIT or proprietary. See [license_details.md](license_details.md).

**3. CC BY-SA (brofjorden, hongkong, russia_meadow)**
Same attribution requirements as CC BY, plus: if you create an adaptation/derivative, you must release it under CC BY-SA or a compatible license. This is the one that needs careful analysis -- see [sharealike_analysis.md](sharealike_analysis.md).

**4. Unlicensed personal photos (nigeria, raghav*, robert_hawaii)**
These have no CC license. Without explicit written permission from the photographer, you cannot include them in a public repo or display them on a website. Options:
- Get written permission (email is fine) specifying allowed uses
- Remove them from the public repo and add to `.gitignore`
- Have the photographer apply a CC license of their choice

## What this means for the MIT license

**The MIT license applies only to your code.** The presence of CC-licensed images in the repo doesn't "infect" your code license. This is well-established practice -- see Linux kernel (GPLv2 code + various firmware licenses), many documentation projects (MIT code + CC docs), etc.

CC itself explicitly says their licenses are not recommended for software, and that software licenses are not recommended for creative works. They're designed to coexist.

## Key risk areas

1. **ShareAlike on output images.** If the analemma overlay on a CC BY-SA photo is a derivative, the output image must be CC BY-SA. This doesn't affect the code, but it affects how you label outputs on the website.

2. **Unlicensed photos in a public repo.** The personal photos (nigeria, raghav*, robert_hawaii) are the biggest immediate legal risk. Get permission or remove them.

3. **Web display = distribution.** Serving an image to a browser is "sharing" under CC definitions. All attribution requirements kick in.

## Files in this research

- [overview.md](overview.md) -- this file
- [sharealike_analysis.md](sharealike_analysis.md) -- deep dive on whether overlays are derivatives under CC BY-SA
- [license_details.md](license_details.md) -- specifics of CC BY 2.0, CC BY 4.0, CC BY-SA 4.0, CC0
- [attribution_guide.md](attribution_guide.md) -- how to attribute on the website and in the repo
- [repo_structure.md](repo_structure.md) -- proposed file layout, NOTICE file, multi-license setup
- [web_display_and_uploads.md](web_display_and_uploads.md) -- legal considerations for the web app
