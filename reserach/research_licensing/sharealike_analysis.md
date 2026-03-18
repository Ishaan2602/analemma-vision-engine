# ShareAlike Analysis -- Is the Analemma Overlay a Derivative Work?

This is the central legal question for this project. Three of the sample images use CC BY-SA 4.0, and ShareAlike requires that *adaptations* (derivative works) be released under the same license. Whether the analemma overlay constitutes an adaptation determines your obligations.

## What CC BY-SA 4.0 says

From the legal code, Section 1(a):

> **Adapted Material** means material subject to Copyright and Similar Rights that is derived from or based upon the Licensed Material and in which the Licensed Material is translated, altered, arranged, transformed, or otherwise modified in a manner requiring permission under the Copyright and Similar Rights held by the Licensor.

And Section 2(a)(4):

> The Licensor authorizes You to exercise the Licensed Rights in all media and formats whether now known or hereafter created, and to make technical modifications necessary to do so. [...] For purposes of this Public License, simply making modifications authorized by this Section 2(a)(4) **never produces Adapted Material.**

So "technical modifications" (format changes, resizing, etc.) are explicitly *not* adaptations. But meaningful creative modifications are.

## What the CC FAQ says about adaptations

From the CC FAQ entry "When is my use considered an adaptation?":

> Whether a modification of licensed material is considered an adaptation for the purpose of CC licenses depends primarily on the **applicable copyright law**. [...] Generally, a modification rises to the level of an adaptation under copyright law when the modified work is **based on the prior work but manifests sufficient new creativity to be copyrightable**.

Key points from the FAQ:
- Format/medium changes are never adaptations under CC 4.0 licenses
- The test is whether the modification adds "sufficient new creativity to be copyrightable"
- It depends on the jurisdiction's copyright law

## Analysis: the analemma overlay

The Analemma Engine takes a photograph and draws a calculated astronomical curve on top of it. The original photograph is reproduced in full. The overlay adds:

- A figure-8 curve representing the sun's position throughout the year
- Potentially date labels, markers, or annotation text
- The curve position is computed from GPS coordinates, timestamp, and camera parameters

**Arguments that this IS an adaptation:**
- The image is modified -- new visual elements are added on top
- The resulting work is "based on" the original photograph
- The overlay involves creative choices (curve style, color, thickness, labels)
- The combined work couldn't exist without the original photo
- Under U.S. copyright's low originality threshold, even minimal creative additions can produce a derivative

**Arguments that this is NOT an adaptation (but a collection/compilation):**
- The photograph is used as-is, in its entirety -- it's not "translated, altered, arranged, or transformed"
- The overlay is a separate layer of data visualization, not a modification of the photograph itself
- The photo serves as a *background* for independently-generated data -- similar to pinning a chart on top of a map
- The creative content (the analemma curve) is purely algorithmic and doesn't engage with the photograph's creative expression
- Analogy: annotating a photograph with text labels or drawing measurement lines doesn't usually create a derivative

## The honest assessment

**This is a gray area, and reasonable people can disagree.** However, the more conservative and safer interpretation is:

**The overlay likely constitutes an adaptation/derivative work.**

Here's why: the resulting image is a single visual work that combines the original photograph with new graphical elements. Under most copyright frameworks (especially U.S. law), this creates a derivative. The fact that the overlay is algorithmically generated doesn't change the analysis -- the resulting combined image is "based on" the original.

The CC FAQ's definition supports this: the original work is "modified in a manner requiring permission under Copyright." You'd need the photographer's copyright permission to modify their photo and distribute the modified version -- and the CC license is what grants that permission.

## What this means in practice

**If the overlay images are derivatives of CC BY-SA photos, then:**

1. The **output images** (photo + overlay) must be shared under CC BY-SA 4.0 (or a compatible license)
2. You must provide attribution (TASL) for the original photo
3. You must indicate that you modified the work
4. You must include a link to the CC BY-SA 4.0 license

**What this does NOT mean:**

1. Your **source code** is NOT affected. The code that *produces* derivatives is not itself a derivative of the images. MIT stays MIT. (Just like how Photoshop isn't a derivative of every photo you edit with it.)
2. Your **other images** are not affected. ShareAlike applies per-image, not to the entire project.
3. **User-uploaded images** are not affected by the sample images' licenses. If a user uploads their own photo and gets an overlay, the output's license depends on whatever license the user's photo carries.

## The practical implication

For the three CC BY-SA sample images:
- When the web app displays the overlaid version, label it **CC BY-SA 4.0**
- Include attribution for the original photographer
- Note that the image was modified ("Analemma curve overlay added by Analemma Engine")

For the CC BY-only sample images:
- The overlay image can be under any license (you could MIT it, CC BY it, or leave it unlicensed)
- You still need attribution for the original photographer
- You still need to note the modification

For the CC0/public domain image:
- No restrictions at all on the output

## Can we MIT-license code that produces CC BY-SA outputs?

**Yes, absolutely.** There's a clean conceptual separation:

- The **code** (calculator, sky mapper, plotter, image anchorer) is your original work, licensed MIT
- The **input images** are others' works, each under their own license
- The **output images** are derivatives of the inputs, and their licensing follows from the input image's license

This is exactly how tools like GIMP, FFmpeg, or ImageMagick work. The tool is under one license (GPL, LGPL, etc.); the outputs depend on the inputs. Nobody argues that GIMP is a derivative of the photos you edit with it.

## Collection vs. adaptation -- the repo itself

One more distinction worth noting: the **repository as a whole** (code + sample images together) is arguably a *collection*, not an adaptation. From the CC FAQ:

> All Creative Commons licenses [...] allow licensed material to be included in collections such as anthologies, encyclopedias, and broadcasts. You may choose a license for the collection, however this does not change the license applicable to the original material.

Your repo is a collection of MIT-licensed code and variously-licensed sample images. You can MIT-license the repo/collection as a whole while each CC image retains its own license. Collections don't trigger ShareAlike -- only adaptations do.

## Sources

- CC BY-SA 4.0 Legal Code, Sections 1(a), 2(a)(4), 3(b): https://creativecommons.org/licenses/by-sa/4.0/legalcode
- CC FAQ, "When is my use considered an adaptation?": https://creativecommons.org/faq/#when-is-my-use-considered-an-adaptation
- CC FAQ, "If I create a collection that includes a work offered under a CC license, which license(s) may I choose for the collection?": https://creativecommons.org/faq/#if-i-create-a-collection-that-includes-a-work-offered-under-a-cc-license-which-licenses-may-i-choose-for-the-collection
- CC FAQ, "If CC SA-licensed content is included in a database, does the entire database have to be licensed under an SA license?": https://creativecommons.org/faq/#if-cc-sa-licensed-content-is-included-in-a-database-does-the-entire-database-have-to-be-licensed-under-an-sa-license
