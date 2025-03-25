from fastapi import APIRouter
from app.api.endpoints import auth, tours, requests

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tours.router, prefix="/tours", tags=["tours"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"]) 