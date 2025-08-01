from fastapi import APIRouter

from .templates import router as templates_router

router = APIRouter(prefix="/collect", tags=["collect"])
router.include_router(templates_router)
