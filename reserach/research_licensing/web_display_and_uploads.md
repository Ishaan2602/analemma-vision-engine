# Web Display, User Uploads, and Terms of Service

Legal considerations for the web application -- displaying CC images, serving overlaid outputs, handling user-uploaded photos, and what terms of service you need.

---

## When a user clicks "Try Sample Image" -- are we distributing a CC image?

**Yes.** Serving an image to a user's browser qualifies as "sharing" under the CC definition. From the CC BY-SA 4.0 legal code:

> **Share** means to provide material to the public by any means or process that requires permission under the Licensed Rights, such as reproduction, public display, public performance, distribution, dissemination, communication, or importation, and to make material available to the public including in ways that members of the public may access the material from a place and at a time individually chosen by them.

That last clause ("from a place and at a time individually chosen by them") describes exactly how a web server works. When your server sends the image bytes to a browser, you're sharing the image.

**What this means:** Every time a sample CC image is displayed on the website, all license obligations apply -- attribution, modification notice (for overlays), and ShareAlike (for CC BY-SA images).

---

## When we display the overlaid version -- is that distributing a derivative?

**Yes.** If the overlay constitutes an adaptation (see [sharealike_analysis.md](sharealike_analysis.md)), then serving the overlaid image is sharing Adapted Material. All the original license conditions apply, plus:

- For CC BY-SA inputs: the overlaid output must be labeled CC BY-SA 4.0
- For CC BY inputs: attribution must note the modification
- For CC0 inputs: no restrictions

---

## Do we need to show the license on the web page where the image appears?

**Yes, or link to it.** The CC licenses require that you "include the text of, or the URI or hyperlink to, this Public License." You can satisfy this with a visible license indicator near the image, or a link to a credits/attribution page.

The CC FAQ confirms: "you may satisfy the attribution requirement by providing a link to a place where the attribution information may be found."

**Practical approach:**

For sample images on the website, show a small attribution line below each image:

```html
<figure>
  <img src="/samples/hongkong_overlay.png" alt="Analemma overlay on Hong Kong harbor photo">
  <figcaption>
    Adapted from "Bright light" by Kailanchoi
    (<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>).
    Overlay by Analemma Engine.
    <a href="/credits">Full credits</a>
  </figcaption>
</figure>
```

This is compact, provides the required information, and links to the full credits page for anyone who wants complete details.

---

## User-uploaded images

### What license applies to images users upload?

Whatever license the user's photo carries. If someone uploads their own photo with no CC license, the output has no CC encumbrances. If someone uploads a CC BY-SA photo, the output would inherit those terms.

Your engine doesn't change this. It's a tool -- the licensing of the output depends on the licensing of the input.

### Do we need a Terms of Service?

**Yes, you should have one.** Not because CC licenses require it, but because you're running a web service that accepts user uploads and produces content. A basic ToS should cover:

1. **User content ownership.** "You retain all rights to images you upload. By uploading, you grant us a temporary license to process the image and return the result."

2. **No storage commitment.** "We do not permanently store uploaded images. Images are processed in memory and discarded after the result is returned." (Or whatever your actual data handling is.)

3. **No responsibility for input licensing.** "You are responsible for ensuring you have the right to upload and modify any images you submit. We are not responsible for copyright violations in user-provided content."

4. **Output licensing.** "The licensing of output images depends on the licensing of the input. Overlays on CC BY-SA images are subject to CC BY-SA terms. Overlays on your own photos are yours."

5. **Disclaimer of warranties.** Standard "as-is" disclaimer.

6. **Use restrictions.** No automated bulk processing, no scraping sample images, etc.

### Template: minimal Terms of Service

```
TERMS OF SERVICE
================

1. The Service

Analemma Engine is a free tool that overlays astronomical analemma curves
onto sky photographs. You can use the provided sample images or upload
your own.

2. Your Content

You retain all rights to images you upload. By uploading an image, you
grant us a temporary, non-exclusive license solely to process the image
and deliver the result to you. We do not store, share, or use your
uploaded images for any other purpose.

3. Your Responsibilities

You represent that you have the right to upload and modify any image you
submit. You are solely responsible for compliance with any copyright or
license terms that apply to your uploaded images.

4. Sample Images

Sample images are provided under Creative Commons licenses. Attribution
and license details are available on our Credits page. Output images
derived from CC BY-SA licensed samples are subject to CC BY-SA 4.0
terms.

5. Output Images

The license terms of output images depend on the input:
  - Your own photos: the output is yours, no restrictions from us
  - CC BY-SA samples: the output is CC BY-SA 4.0
  - CC BY samples: attribution to the original photographer is required
  - CC0 samples: no restrictions

6. No Warranty

This service is provided "as is" without warranty of any kind. We are
not liable for any damages arising from your use of the service.

7. Changes

We may update these terms at any time. Continued use constitutes
acceptance of updated terms.
```

### Should we state that we don't store user images?

**Yes, if it's true.** This is both a privacy measure and a trust signal. If your processing pipeline genuinely discards uploads after returning the result, say so clearly. Users are (rightly) cautious about uploading photos to random websites.

If the API processes images in memory via FastAPI's `UploadFile` and doesn't write to disk or a database, you can truthfully state:

> "Uploaded images are processed in memory and are not stored on our servers. No copies are retained after processing is complete."

If you do cache results temporarily (e.g., for a "download" link), be specific about the retention period.

---

## Privacy considerations

Even though this isn't a social platform, GDPR and similar laws may apply if:
- The images contain identifiable people
- You collect any user data (IP addresses, usage analytics)
- Users are in the EU

For a minimal tool like this, a short privacy policy covering what data you collect (likely: nothing beyond standard server logs) and what you don't store (uploaded images) is sufficient. Don't overcomplicate it.

---

## Summary of web obligations by image type

| Image source | Display original | Display overlay | Attribution needed | License label | ShareAlike |
|---|---|---|---|---|---|
| CC BY-SA sample | Show with attribution | Show with attribution + modification note | Yes | CC BY-SA 4.0 | Yes (overlay = CC BY-SA) |
| CC BY sample | Show with attribution | Show with attribution + modification note | Yes | CC BY 2.0 / 4.0 | No |
| CC0 sample | Show freely | Show freely | No (recommended) | CC0 | No |
| User's own photo | N/A (not stored) | Return to user only | No | None | No |
| User's CC-licensed photo | N/A (not stored) | Return to user only | N/A (user's responsibility) | N/A | N/A |
