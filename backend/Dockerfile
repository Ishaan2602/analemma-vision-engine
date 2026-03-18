FROM python:3.12-slim

WORKDIR /app

# Install system deps for Pillow and pillow-heif
RUN apt-get update && apt-get install -y --no-install-recommends \
    libheif-dev \
    libffi-dev \
    libjpeg62-turbo-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the JPL DE440 ephemeris (~17 MB) so it doesn't
# happen on the first request or on every cold start
RUN python -c "from astropy.coordinates import get_sun; from astropy.time import Time; get_sun(Time('2025-01-01'))"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
