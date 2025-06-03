from fastapi import APIRouter

from app.api.v1.endpoints import presells

api_router = APIRouter()
api_router.include_router(presells.router, prefix="/presells", tags=["presells"])
