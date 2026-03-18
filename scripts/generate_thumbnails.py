"""Generate thumbnail images for the sample gallery.

Reads the original images from input_images/ and writes resized
copies (1200px wide, JPEG quality 90) to frontend/static/samples/.
Applies EXIF orientation before resizing so the thumbnail matches
what the engine sees after exif_transpose.
"""

from pathlib import Path
from PIL import Image, ImageOps

SAMPLES = {
    "brofjorden": "brofjorden.jpg",
    "cold_canada": "cold_canada.jpg",
    "hongkong": "hongkong_img.jpeg",
    "hunan": "hunan.jpg",
    "sharjah_sands": "Sun_in_the_sands.jpg",
    "russia_meadow": "russia_meadow.jpg",
}

INPUT_DIR = Path(__file__).parent.parent / "input_images"
OUTPUT_DIR = Path(__file__).parent.parent / "frontend" / "static" / "samples"

TARGET_WIDTH = 1200


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for sample_id, filename in SAMPLES.items():
        src = INPUT_DIR / sample_id / filename
        if not src.exists():
            print(f"SKIP {sample_id}: {src} not found")
            continue

        img = Image.open(src)

        # Apply EXIF orientation first (critical for images with rotation tags)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        img = img.convert("RGB")

        # Resize proportionally
        ratio = TARGET_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((TARGET_WIDTH, new_height), Image.LANCZOS)

        out = OUTPUT_DIR / f"{sample_id}_thumb.jpg"
        img.save(out, "JPEG", quality=90)
        print(f"OK {sample_id}: {img.width}x{img.height} -> {out}")


if __name__ == "__main__":
    main()
