# Usage Guide

## Installation

```bash
cd analemma_project
pip install -r requirements.txt
```

Python 3.10+. All dependencies (numpy, matplotlib, astropy, scipy, Pillow, timezonefinder, pandas, plotly) are installed via requirements.txt.

## Processing a sky photo

The fastest way to get an overlay:

```bash
python create_input.py myimage --image path/to/photo.jpg
# Edit input_images/myimage/metadata.txt with coordinates, datetime, camera specs
python demo_scripts/process_image.py myimage
```

This auto-detects the sun, computes the analemma for that time of day, and writes three files to `output/myimage_output/`:
- `myimage_overlay.png` -- analemma curve on top of the original photo
- `myimage_sky_chart.png` -- altitude vs azimuth scatter plot
- `myimage_composite.png` -- both side by side

## Python API

### Three-layer pipeline

```python
from analemma import AnalemmaCalculator, SkyMapper, AnalemmaPlotter

calc = AnalemmaCalculator(mode='high-precision', year=2026)
sky = SkyMapper(latitude=40.1, longitude=-88.2)
plotter = AnalemmaPlotter()

data = calc.calculate_year(hour=15, minute=0)
mapped = sky.map_to_horizon(data)
plotter.plot_analemma(mapped, title='UIUC 3PM')
plotter.show()
```

`AnalemmaCalculator` computes declination and equation of time for each day. `SkyMapper` converts those to altitude/azimuth for the observer's location. `AnalemmaPlotter` renders the result.

Two calculation modes: `'approximate'` uses Spencer (1971) analytical formulas, `'high-precision'` uses Astropy with JPL DE440 ephemeris. HP mode is recommended for overlays.

### Image overlay (manual)

```python
from datetime import datetime
from analemma.image_anchor import ImageAnchorer

anchorer = ImageAnchorer(
    image_path='input_images/hongkong/hongkong_img.jpeg',
    anchor_datetime=datetime(2014, 9, 2, 16, 20, 48),
    latitude=22.3,
    longitude=114.2,
    auto_detect_sun=True
)

anchorer.calibrate_from_focal_length(
    focal_length_mm=6.1,
    sensor_width_mm=6.2,
    sensor_height_mm=4.6
)

result = anchorer.overlay_analemma(output_path='hongkong_overlay.png')
print(f"Points drawn: {result['points_drawn']}")
```

You can also pass `sun_pixel=(x, y)` instead of `auto_detect_sun=True` to manually specify the sun's position.

### Plot types

```python
plotter.plot_analemma(sky_data)      # Alt vs Az (sky chart)
plotter.plot_figure8(calc_data)      # EoT vs Declination
plotter.plot_time_series(calc_data)  # Dec and EoT over the year
plotter.plot_sky_dome(sky_data)      # Polar projection
plotter.plot_interactive(sky_data)   # Plotly interactive (opens browser)
plotter.plot_comparison(approx, hp)  # Side-by-side mode comparison
```

## CLI

```bash
python analemma_cli.py calculate --lat 40.1 --lon -88.2 --hour 12 --plot --show
python analemma_cli.py compare --lat 40.1 --lon -88.2 --plot
python analemma_cli.py anchor --image photo.jpg --datetime "2026-06-21 12:00" --lat 40.1 --lon -88.2 --focal-length 24
```

Run `python analemma_cli.py --help` for full options.

## Metadata format

Each input image folder needs a `metadata.txt` with KEY=VALUE pairs:

```
IMAGE_FILE=photo.jpg
DATETIME=2024-06-15 14:30:00
LATITUDE=40.1
LONGITUDE=-88.2W
FOCAL_LENGTH_MM=5.7
SENSOR_WIDTH_MM=7.8
SENSOR_HEIGHT_MM=5.8
CAMERA_MAKE=Apple
CAMERA_MODEL=iPhone 14
LOCATION_NAME=Campus
```

Coordinates accept multiple formats: `40.1`, `-88.2`, `40.1N`, `88.2W`, `8 48 26.98 E`, `8deg 48' 26.98" E`. See [METADATA_REFERENCE.md](METADATA_REFERENCE.md) for full details on sensor size, focal length, and the crop factor method.

## Timezone handling

Timezone is auto-detected from GPS coordinates using the IANA database (`timezonefinder` + `zoneinfo`). DST is handled correctly based on the photo's datetime. You can override it with `TIMEZONE_OFFSET=-10` in metadata if needed.

## Local testing (web app)

To run the web app locally instead of using analemmavision.app:

**Backend** (requires Python 3.12+):

```bash
cd backend
pip install -r requirements.txt
python -c "from astropy.coordinates import solar_system_ephemeris; solar_system_ephemeris.set('jpl')"  # one-time ephemeris download
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be at `http://localhost:8000`. Test with `curl http://localhost:8000/api/health`.

**Frontend** (requires Node 18+):

```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

On Windows (PowerShell): `$env:VITE_API_URL="http://localhost:8000"; npm run dev`

Open `http://localhost:5173` in the browser. The frontend talks to your local backend instead of the production API.

## Troubleshooting

If you get import errors, make sure you're running from the project root or add it to your path:

```bash
cd analemma_project
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Astropy will download the JPL DE440 ephemeris on first use of high-precision mode (~16 MB). Needs internet for that initial download.

- **examples/**: Runnable example scripts
- **tests/**: Unit tests and validation
- OpenCV Camera Calibration: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
- Brown-Conrady Distortion Model: https://en.wikipedia.org/wiki/Distortion_(optics)

## Contributing

This is an educational/research project. Contributions welcome!

---

**Note**: This project does not currently have a license. All rights reserved.
