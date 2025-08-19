from fastapi import APIRouter

from .companies import router as companies_router

router = APIRouter(prefix="/base", tags=["base"])
router.include_router(companies_router)
