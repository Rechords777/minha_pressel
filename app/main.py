import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Request, staticfiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine, Base

# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS - Forçando CORS global para permitir qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Define paths for generated assets
GENERATED_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generated_assets")
HTML_PRESELLS_DIR = os.path.join(GENERATED_ASSETS_DIR, "html_presells")
SCREENSHOTS_DIR = os.path.join(GENERATED_ASSETS_DIR, "screenshots")

# Ensure directories exist
os.makedirs(HTML_PRESELLS_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Add to settings for use in other modules
settings.GENERATED_ASSETS_DIR = GENERATED_ASSETS_DIR

# Mount static files for presells
app.mount("/presells", staticfiles.StaticFiles(directory=HTML_PRESELLS_DIR), name="presells")
app.mount("/screenshots", staticfiles.StaticFiles(directory=SCREENSHOTS_DIR), name="screenshots")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Presell Platform API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
