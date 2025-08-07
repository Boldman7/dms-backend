from fastapi import APIRouter

from .templates import router as templates_router
from .smart_hardware_types import router as smart_hardware_types_router
from .groups import router as groups_router
from .plc_brand import router as plc_brand_router

router = APIRouter(prefix="/collect", tags=["collect"])
router.include_router(templates_router)
router.include_router(smart_hardware_types_router)
router.include_router(groups_router)
router.include_router(plc_brand_router)
