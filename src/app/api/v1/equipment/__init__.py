from fastapi import APIRouter

from .products import router as products_router

router = APIRouter(prefix="/equipment", tags=["equipment"])
router.include_router(products_router)
