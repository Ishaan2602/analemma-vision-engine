# Proposed Repo Structure for Multi-License Setup

How to organize the repository so that the MIT license covers the code and the CC licenses are clearly associated with their respective images.

---

## Proposed structure

```
analemma_project/
    LICENSE                     <-- MIT License (covers code only)
    NOTICE                      <-- Third-party content credits & licenses
    README.md                   <-- Mention multi-license setup, point to NOTICE
    requirements.txt
    analemma/                   <-- MIT-licensed code
    demo_scripts/               <-- MIT-licensed code
    examples/                   <-- MIT-licensed code
    tests/                      <-- MIT-licensed code
    docs/                       <-- MIT-licensed (or CC BY 4.0 for docs)
    input_images/               <-- NOT covered by MIT
        README.md               <-- Explains image licensing
        brofjorden/
            metadata.txt        <-- Already contains license info
            [image file]
        cold_canada/
            metadata.txt
            [image file]
        ...
    output/                     <-- License depends on input image
```

The key changes from current state:
1. Add a `LICENSE` file (MIT) at the root
2. Add a `NOTICE` file listing all third-party content
3. Add a `README.md` inside `input_images/` explaining that images are not MIT-licensed
4. Remove or `.gitignore` unlicensed personal photos (nigeria, raghav*, robert_hawaii)

---

## Template: LICENSE file (root)

```
MIT License

Copyright (c) 2025-2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

Note: This license applies to the source code and documentation of the
Analemma Engine. Sample images in the input_images/ directory are provided
under their own licenses (primarily Creative Commons). See the NOTICE file
for details.
```

---

## Template: NOTICE file (root)

```
THIRD-PARTY CONTENT NOTICE
===========================

The Analemma Engine source code is licensed under the MIT License.
See the LICENSE file for details.

This project includes sample sky photographs from Wikimedia Commons,
provided under the Creative Commons licenses listed below. These images
are NOT covered by the MIT License.


SAMPLE IMAGES
-------------

brofjorden/
  Title:   "Waining sun dog with reflection over Brofjorden"
  Author:  W.carter
  License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
           https://creativecommons.org/licenses/by-sa/4.0/
  Source:  https://commons.wikimedia.org/wiki/File:Waining_sun_dog_with_reflection_over_Brofjorden.jpg

cold_canada/
  Title:   "Cold Sun Landscape"
  Author:  Emmanuel Huybrechts
  License: Creative Commons Attribution 2.0 Generic (CC BY 2.0)
           https://creativecommons.org/licenses/by/2.0/
  Source:  https://commons.wikimedia.org/wiki/File:Cold_Sun_Landscape_(4698301386).jpg

hongkong/
  Title:   "Bright light"
  Author:  Kailanchoi
  License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
           https://creativecommons.org/licenses/by-sa/4.0/
  Source:  https://commons.wikimedia.org/wiki/File:Bright_light.JPG

hunan/
  Title:   "Landscape with Rising Sun in Dongkou County"
  Author:  Huangdan2060
  License: Creative Commons CC0 1.0 Universal Public Domain Dedication
           https://creativecommons.org/publicdomain/zero/1.0/
  Source:  https://commons.wikimedia.org/wiki/File:Landscape_with_Rising_Sun_in_Dongkou_County.jpg

russia_meadow/
  Title:   "Ostringen - Tiefenbach - Kreuzbergkapelle -
           Situationsansicht von Osten bei Sonnenuntergang"
  Author:  Roman Eisele
  License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
           https://creativecommons.org/licenses/by-sa/4.0/
  Source:  https://commons.wikimedia.org/wiki/File:Östringen_-_Tiefenbach_-_Kreuzbergkapelle_-_Situationsansicht_von_Osten_bei_Sonnenuntergang.jpg

sharjah_sands/
  Title:   "Sun in the sands"
  Author:  Aleksandr Serebrennikov
  License: Creative Commons Attribution 4.0 International (CC BY 4.0)
           https://creativecommons.org/licenses/by/4.0/
  Source:  https://commons.wikimedia.org/wiki/File:Sun_in_the_sands.jpg


OUTPUT IMAGES
-------------

Output images in the output/ directory are derivatives of the corresponding
input images. Their licensing depends on the input image's license:

  - Outputs derived from CC BY-SA 4.0 images are licensed under CC BY-SA 4.0.
  - Outputs derived from CC BY 2.0 or CC BY 4.0 images carry the original
    attribution requirements but may be used under any compatible terms.
  - Outputs derived from CC0 images have no license restrictions.

All output images have been modified from the originals by the addition
of a computed analemma curve overlay by the Analemma Engine.
```

---

## Template: input_images/README.md

```markdown
# Sample Images

These photographs are provided as sample inputs for the Analemma Engine.
They are sourced from Wikimedia Commons and are **NOT covered by the
project's MIT License**.

Each image is licensed under its own Creative Commons license, as noted
in the corresponding metadata.txt file and in the project's NOTICE file.

If you redistribute this project, you must comply with the license terms
for each image you include. See the NOTICE file at the project root for
full attribution details.
```

---

## What to do with unlicensed images

The images in `nigeria/`, `raghav/`, `raghav2/`, `raghav6/`, and `robert_hawaii/` have no CC license. Options:

**Option 1 (recommended): Remove from the public repo**
Add them to `.gitignore`. Keep them locally for development. The public repo should only contain properly licensed material.

**Option 2: Get permission**
Contact each photographer and get written permission to include the photos. Ideally, have them choose a CC license. An email saying "yes, you can use it" is legally weak compared to a specific CC license grant.

**Option 3: Replace with CC-licensed alternatives**
Find similar sky photos on Wikimedia Commons with CC BY or CC0 licenses.

---

## How other projects handle this

**Linux kernel:** GPLv2 code + binary firmware blobs under various licenses. Firmware is in a separate `firmware/` directory with its own `WHENCE` file listing each blob's license.

**Mozilla Firefox:** MPL 2.0 code + third-party libraries under MIT/BSD/Apache. Uses a `LICENSE` file at root and per-directory licenses where needed.

**Wikipedia/MediaWiki:** GPLv2 code. User-contributed content is CC BY-SA. Clean separation between software license and content license.

The pattern is consistent: put the primary license at the root, document third-party licenses in NOTICE or a similar file, and keep clear boundaries between code and content.
