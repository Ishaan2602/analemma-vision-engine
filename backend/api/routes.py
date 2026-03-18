from typing import Optional

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import Response

from .engine_wrapper import analyze_image, render_overlay
from .schemas import AnalyzeResponse, SampleImage

router = APIRouter(prefix="/api")

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.heic', '.heif', '.png', '.webp'}
MAX_FILE_SIZE = 30 * 1024 * 1024  # 30 MB

SAMPLE_IMAGES: list[SampleImage] = [
    SampleImage(
        id='brofjorden',
        name='Brofjorden, Sweden',
        thumbnail='/samples/brofjorden_thumb.jpg',
        datetime='2016-09-05T19:38:15',
        latitude=58.373236,
        longitude=11.446522,
        focal_length_mm=17.4,
        sensor_width_mm=13.2,
        sensor_height_mm=8.8,
        license='CC BY-SA 4.0',
        author='W.carter',
    ),
    SampleImage(
        id='cold_canada',
        name='Quebec, Canada',
        thumbnail='/samples/cold_canada_thumb.jpg',
        datetime='2009-12-20T10:53:00',
        latitude=46.809397,
        longitude=-71.2077,
        focal_length_mm=24.0,
        sensor_width_mm=23.4,
        sensor_height_mm=15.6,
        license='CC BY 2.0',
        author='Emmanuel Huybrechts',
    ),
    SampleImage(
        id='hongkong',
        name='Hong Kong Harbor',
        thumbnail='/samples/hongkong_thumb.jpg',
        datetime='2014-09-02T16:20:48',
        latitude=22.3,
        longitude=114.2,
        focal_length_mm=6.1,
        sensor_width_mm=7.4,
        sensor_height_mm=5.5,
        license='CC BY-SA 4.0',
        author='Wikimedia Commons',
    ),
    SampleImage(
        id='hunan',
        name='Hunan, China',
        thumbnail='/samples/hunan_thumb.jpg',
        datetime='2017-12-18T08:25:14',
        latitude=27.042819,
        longitude=110.598294,
        focal_length_mm=3.95,
        sensor_width_mm=5.6,
        sensor_height_mm=4.2,
        license='CC BY-SA 4.0',
        author='Wikimedia Commons',
    ),
    SampleImage(
        id='sharjah_sands',
        name='Sharjah, UAE',
        thumbnail='/samples/sharjah_sands_thumb.jpg',
        datetime='2022-05-27T18:40:00',
        latitude=25.3,
        longitude=55.5,
        focal_length_mm=18.0,
        sensor_width_mm=23.6,
        sensor_height_mm=15.6,
        license='CC BY 4.0',
        author='Wikimedia Commons',
    ),
    SampleImage(
        id='russia_meadow',
        name='Russia Meadow',
        thumbnail='/samples/russia_meadow_thumb.jpg',
        datetime='2020-12-29T19:35:00',
        latitude=49.1713,
        longitude=8.807494,
        focal_length_mm=35.0,
        sensor_width_mm=35.9,
        sensor_height_mm=24.0,
        license='CC BY-SA 4.0',
        author='Wikimedia Commons',
    ),
]


def _validate_file(file: UploadFile) -> None:
    filename = (file.filename or '').lower()
    ext = '.' + filename.rsplit('.', 1)[-1] if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: JPEG, HEIC, PNG, WebP.",
        )


@router.post("/analyze", response_model=AnalyzeResponse)
async def api_analyze(
    file: UploadFile,
    latitude: float = Form(...),
    longitude: float = Form(...),
    datetime_str: str = Form(...),
    focal_length_mm: float = Form(...),
    sensor_width_mm: float = Form(...),
    sensor_height_mm: float = Form(...),
    sun_x: Optional[int] = Form(None),
    sun_y: Optional[int] = Form(None),
):
    _validate_file(file)
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 30 MB limit.")

    try:
        result = await analyze_image(
            file_bytes=file_bytes,
            filename=file.filename or 'upload.jpg',
            latitude=latitude,
            longitude=longitude,
            datetime_str=datetime_str,
            focal_length_mm=focal_length_mm,
            sensor_width_mm=sensor_width_mm,
            sensor_height_mm=sensor_height_mm,
            sun_x=sun_x,
            sun_y=sun_y,
        )
        return result
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your image.",
        )


@router.post("/render")
async def api_render(
    file: UploadFile,
    latitude: float = Form(...),
    longitude: float = Form(...),
    datetime_str: str = Form(...),
    focal_length_mm: float = Form(...),
    sensor_width_mm: float = Form(...),
    sensor_height_mm: float = Form(...),
    sun_x: Optional[int] = Form(None),
    sun_y: Optional[int] = Form(None),
):
    _validate_file(file)
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 30 MB limit.")

    try:
        png_bytes = await render_overlay(
            file_bytes=file_bytes,
            filename=file.filename or 'upload.jpg',
            latitude=latitude,
            longitude=longitude,
            datetime_str=datetime_str,
            focal_length_mm=focal_length_mm,
            sensor_width_mm=sensor_width_mm,
            sensor_height_mm=sensor_height_mm,
            sun_x=sun_x,
            sun_y=sun_y,
        )
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=analemma_overlay.png"},
        )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while rendering the overlay.",
        )


@router.get("/samples", response_model=list[SampleImage])
async def api_samples():
    return SAMPLE_IMAGES
