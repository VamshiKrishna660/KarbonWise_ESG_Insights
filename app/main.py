from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine
from app import models
from app.routers import upload, records, insights

# Create all DB tables on startup (Alembic handles migrations in production)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KarbonWise ESG Data Extraction API",
    description=(
        "A REST API that accepts PDF and Excel sustainability reports, "
        "extracts structured ESG metrics using Google Gemini, and exposes "
        "endpoints to query and summarize the data."
    ),
    version="1.0.0",
    contact={"name": "KarbonWise Engineering"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload.router)
app.include_router(records.router)
app.include_router(insights.router)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/", tags=["UI"])
async def read_index():
    """Serve the frontend dashboard index page."""
    return FileResponse(os.path.join(static_path, "index.html"))


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "KarbonWise ESG API is running."}
