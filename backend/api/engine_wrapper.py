import asyncio
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pillow_heif

pillow_heif.register_heif_opener()

_executor = ThreadPoolExecutor(max_workers=2)


def _run_analyze(tmp_path: str, latitude: float, longitude: float,
                 anchor_dt: datetime, focal_length_mm: float,
                 sensor_width_mm: float, sensor_height_mm: float,
                 sun_pixel: tuple | None) -> dict:
    """Synchronous helper -- runs in a separate process."""
    from analemma.image_anchor import ImageAnchorer

    anchorer = ImageAnchorer(
        image_path=tmp_path,
        anchor_datetime=anchor_dt,
        latitude=latitude,
        longitude=longitude,
        sun_pixel=sun_pixel,
        mode='high-precision',
    )
    anchorer.calibrate_from_focal_length(
        focal_length_mm, sensor_width_mm, sensor_height_mm
    )
    points = anchorer.generate_analemma_points()

    # Filter to in-bounds points only
    w, h = anchorer.image_width, anchorer.image_height
    filtered = []
    for p in points:
        px, py = p['pixel_x'], p['pixel_y']
        if 0 <= px < w and 0 <= py < h:
            filtered.append({
                'pixel_x': px,
                'pixel_y': py,
                'date': p['date'].strftime('%Y-%m-%d'),
                'altitude': round(p['altitude'], 2),
                'azimuth': round(p['azimuth'], 2),
            })

    tz_name = ''
    if anchorer.sky_mapper._iana_timezone_name:
        tz_name = anchorer.sky_mapper._iana_timezone_name
    else:
        tz_name = f"UTC{anchorer.sky_mapper.timezone_offset:+.1f}"

    return {
        'image_width': w,
        'image_height': h,
        'anchor_point': {
            'pixel_x': anchorer.sun_pixel[0],
            'pixel_y': anchorer.sun_pixel[1],
            'date': anchorer.anchor_datetime.strftime('%Y-%m-%d'),
            'altitude': round(anchorer.anchor_data['altitude'], 2),
            'azimuth': round(anchorer.anchor_data['azimuth'], 2),
        },
        'points': filtered,
        'metadata': {
            'latitude': latitude,
            'longitude': longitude,
            'timezone': tz_name,
            'time_of_day': anchorer.anchor_datetime.strftime('%H:%M'),
        },
    }


def _run_render(tmp_path: str, latitude: float, longitude: float,
                anchor_dt: datetime, focal_length_mm: float,
                sensor_width_mm: float, sensor_height_mm: float,
                sun_pixel: tuple | None) -> bytes:
    """Synchronous helper -- runs in a separate process."""
    from analemma.image_anchor import ImageAnchorer

    anchorer = ImageAnchorer(
        image_path=tmp_path,
        anchor_datetime=anchor_dt,
        latitude=latitude,
        longitude=longitude,
        sun_pixel=sun_pixel,
        mode='high-precision',
    )
    anchorer.calibrate_from_focal_length(
        focal_length_mm, sensor_width_mm, sensor_height_mm
    )

    out_fd, out_path = tempfile.mkstemp(suffix='.png')
    os.close(out_fd)
    try:
        anchorer.overlay_analemma(output_path=out_path)
        with open(out_path, 'rb') as f:
            return f.read()
    finally:
        if os.path.exists(out_path):
            os.unlink(out_path)


def _parse_inputs(file_bytes: bytes, filename: str, datetime_str: str,
                  sun_x: int | None, sun_y: int | None):
    """Write bytes to a temp file and parse the datetime string."""
    suffix = os.path.splitext(filename)[1] or '.jpg'
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    os.write(fd, file_bytes)
    os.close(fd)

    anchor_dt = datetime.fromisoformat(datetime_str)
    sun_pixel = (sun_x, sun_y) if sun_x is not None and sun_y is not None else None
    return tmp_path, anchor_dt, sun_pixel


async def analyze_image(file_bytes: bytes, filename: str,
                        latitude: float, longitude: float,
                        datetime_str: str, focal_length_mm: float,
                        sensor_width_mm: float, sensor_height_mm: float,
                        sun_x: int | None = None,
                        sun_y: int | None = None) -> dict:
    tmp_path, anchor_dt, sun_pixel = _parse_inputs(
        file_bytes, filename, datetime_str, sun_x, sun_y
    )
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            _executor, _run_analyze,
            tmp_path, latitude, longitude, anchor_dt,
            focal_length_mm, sensor_width_mm, sensor_height_mm, sun_pixel,
        )
        return result
    except ValueError as e:
        raise ValueError(
            "Could not detect the sun in this image. "
            "Try specifying the sun position manually."
        ) from e
    except RuntimeError as e:
        raise RuntimeError(
            "Calculation error. Please check your date/time and coordinates."
        ) from e
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _run_charts(latitude: float, longitude: float,
                hour: int, minute: int) -> dict:
    """Generate sky chart and figure-8 as base64 PNGs."""
    import base64
    import io

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    from analemma.calculator import AnalemmaCalculator
    from analemma.sky_mapper import SkyMapper
    from analemma.plotter import AnalemmaPlotter

    calc = AnalemmaCalculator(mode='high-precision')
    calc_data = calc.calculate_year(hour=hour, minute=minute)

    sky = SkyMapper(latitude=latitude, longitude=longitude)
    sky_data = sky.map_to_horizon(calc_data)

    plotter = AnalemmaPlotter(figure_size=(8, 6))

    # Sky chart
    fig_sky = plotter.plot_analemma(sky_data,
        title=f'Sky Chart -- {latitude:.1f}, {longitude:.1f} at {hour:02d}:{minute:02d}')
    buf_sky = io.BytesIO()
    fig_sky.savefig(buf_sky, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig_sky)
    buf_sky.seek(0)
    sky_b64 = base64.b64encode(buf_sky.read()).decode('ascii')

    # Figure-8
    fig_f8 = plotter.plot_figure8(calc_data,
        title='Analemma Figure-8 (EoT vs Declination)')
    buf_f8 = io.BytesIO()
    fig_f8.savefig(buf_f8, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig_f8)
    buf_f8.seek(0)
    f8_b64 = base64.b64encode(buf_f8.read()).decode('ascii')

    return {'sky_chart': sky_b64, 'figure8': f8_b64}


async def generate_charts(latitude: float, longitude: float,
                          datetime_str: str) -> dict:
    anchor_dt = datetime.fromisoformat(datetime_str)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor, _run_charts,
        latitude, longitude, anchor_dt.hour, anchor_dt.minute,
    )


async def render_overlay(file_bytes: bytes, filename: str,
                         latitude: float, longitude: float,
                         datetime_str: str, focal_length_mm: float,
                         sensor_width_mm: float, sensor_height_mm: float,
                         sun_x: int | None = None,
                         sun_y: int | None = None) -> bytes:
    tmp_path, anchor_dt, sun_pixel = _parse_inputs(
        file_bytes, filename, datetime_str, sun_x, sun_y
    )
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            _executor, _run_render,
            tmp_path, latitude, longitude, anchor_dt,
            focal_length_mm, sensor_width_mm, sensor_height_mm, sun_pixel,
        )
        return result
    except ValueError as e:
        raise ValueError(
            "Could not detect the sun in this image. "
            "Try specifying the sun position manually."
        ) from e
    except RuntimeError as e:
        raise RuntimeError(
            "Calculation error. Please check your date/time and coordinates."
        ) from e
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
