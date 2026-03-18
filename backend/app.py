from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Analemma Vision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Dev frontend
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
