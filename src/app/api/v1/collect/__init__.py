from fastapi import APIRouter

from .templates import router as templates_router
from .smart_hardware_types import router as smart_hardware_types_router
from .groups import router as groups_router
from .plc_brands import router as plc_brand_router
from .plc_types import router as plc_type_router
from .variables import router as variables_router
from .smart_hardwares import router as smart_hardwares_router
from .connections import router as connections_router
from .template_connections import router as template_connections_router

router = APIRouter(prefix="/collect", tags=["collect"])
router.include_router(templates_router)
router.include_router(smart_hardware_types_router)
router.include_router(groups_router)
router.include_router(plc_brand_router)
router.include_router(plc_type_router)
router.include_router(variables_router)
router.include_router(smart_hardwares_router)
router.include_router(connections_router)
router.include_router(template_connections_router)
