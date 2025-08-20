from fastapi import APIRouter

from .licenses import router as licenses_router

router = APIRouter(prefix="/permission", tags=["permission"])
router.include_router(licenses_router)
