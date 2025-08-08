from fastapi import APIRouter

from .products import router as products_router
from .data_sources import router as data_sources_router
from .product_groups import router as product_groups_router

router = APIRouter(prefix="/equipment", tags=["equipment"])
router.include_router(products_router)
router.include_router(data_sources_router)
router.include_router(product_groups_router)
