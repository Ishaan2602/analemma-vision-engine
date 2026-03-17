# Analemma Vision Engine

A Python toolkit for calculating and visualizing the Sun's analemma -- the figure-8 path traced when the Sun is photographed at the same time each day throughout a year -- overlaid onto **real sky photographs**.

## What it does

Given a sky photo with basic metadata (GPS coordinates, timestamp, camera specs), this engine:

1. Detects the sun in the image using progressive thresholding and blob analysis
2. Computes the theoretical analemma curve for that location, time of day, and year
3. Overlays the curve onto the original photo, anchored at the detected sun position

The analemma shape comes from Earth's 23.45-degree axial tilt combined with its elliptical orbit. The engine handles the orbital mechanics, coordinate transforms, timezone detection, and camera projection math.

![Example Output](image.png)

## Installation

```bash
git clone https://github.com/yourusername/analemma_project.git
cd analemma_project
pip install -r requirements.txt
```

Requires Python 3.10+. Key dependencies: astropy, scipy, numpy, matplotlib, Pillow, timezonefinder.

## Quick start

**Process a sky photo:**
```bash
python create_input.py myimage --image path/to/photo.jpg
# Edit input_images/myimage/metadata.txt with location, datetime, camera specs
python demo_scripts/process_image.py myimage
```

**Python API:**
```python
from analemma import AnalemmaCalculator, SkyMapper, AnalemmaPlotter

calc = AnalemmaCalculator(mode='high-precision', year=2025)
sky = SkyMapper(latitude=40.1, longitude=-88.2)
plotter = AnalemmaPlotter()

data = calc.calculate_year(hour=17, minute=42)
mapped = sky.map_to_horizon(data)
plotter.plot_analemma(mapped)
plotter.show()
```

## Architecture

Three-layer pipeline, plus an image overlay layer that composes them:

- **AnalemmaCalculator** -- Solar position math. Two modes: approximate (analytical formulas) and high-precision (Astropy + JPL DE440 ephemeris).
- **SkyMapper** -- Transforms celestial coordinates to horizon coordinates (altitude/azimuth) for a given observer location. Auto-detects timezone via IANA database with DST support.
- **AnalemmaPlotter** -- Matplotlib visualizations: sky charts, figure-8 diagrams, side-by-side comparisons.
- **ImageAnchorer** -- CV pipeline for sun detection, camera projection, and overlay rendering.

## Sun detection

The CV pipeline uses progressive thresholding (starting at 99.9% brightness, lowering to 96%) with scipy's connected-component labeling to find the sun blob. For large saturated blobs, a Gaussian-blurred luminance peak locates the sun center. Adaptive sigma scaling handles everything from small sun disks to massive overexposed glare regions. EXIF orientation is applied automatically.

## Coordinate parsing

Metadata files support flexible coordinate formats:
- Decimal: `40.1`, `-88.2`
- With direction: `40.1N`, `88.2W`, `2.2945E`
- DMS: `8 48 26.98 E`, `8° 48' 26.98" E`

## Project structure

```
analemma/          Core engine modules
input_images/      Photo folders with metadata.txt files
output/            Generated overlay images
demo_scripts/      Processing scripts
examples/          Example usage
docs/              Technical docs, session logs
analysis.ipynb     Interactive testing notebook
```

## Limitations

The image overlay assumes a pinhole camera model. Real lenses have radial distortion that causes slight inaccuracies near image edges. The `cos(altitude)` correction for azimuth compression is applied, but wide-angle shots at extreme altitudes will still show some shape distortion. See [docs/THEORY_AND_LIMITATIONS.md](docs/THEORY_AND_LIMITATIONS.md) for details.
