from fastapi import APIRouter

from .licenses import router as licenses_router
from .records import router as records_router
from .roles import router as roles_router
from .resources import router as resources_router

router = APIRouter(prefix="/permission", tags=["permission"])
router.include_router(licenses_router)
router.include_router(records_router)
router.include_router(roles_router)
router.include_router(resources_router)
