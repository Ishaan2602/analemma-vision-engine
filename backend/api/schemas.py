from typing import Optional

from pydantic import BaseModel


class AnchorPoint(BaseModel):
    pixel_x: int
    pixel_y: int
    date: str
    altitude: float
    azimuth: float


class AnalemmaPoint(BaseModel):
    pixel_x: int
    pixel_y: int
    date: str
    altitude: float
    azimuth: float


class AnalemmaMetadata(BaseModel):
    latitude: float
    longitude: float
    timezone: str
    time_of_day: str


class AnalyzeResponse(BaseModel):
    image_width: int
    image_height: int
    anchor_point: AnchorPoint
    points: list[AnalemmaPoint]
    metadata: AnalemmaMetadata


class SampleImage(BaseModel):
    id: str
    name: str
    thumbnail: str
    datetime: str
    latitude: float
    longitude: float
    focal_length_mm: float
    sensor_width_mm: float
    sensor_height_mm: float
    license: str
    author: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
