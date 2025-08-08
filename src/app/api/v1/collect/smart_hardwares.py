from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_smart_hardwares import crud_smart_hardwares
from ....schemas.smart_hardware import SmartHardwareCreate, SmartHardwareCreateInternal, SmartHardwareRead, SmartHardwareUpdate

router = APIRouter(tags=["smart_hardwares"])


@router.post("/smart-hardware", status_code=201)
async def write_smart_hardware(
    request: Request, smart_hardware: SmartHardwareCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> SmartHardwareRead:
    smart_hardware_internal_dict = smart_hardware.model_dump()
    db_smart_hardware = await crud_smart_hardwares.exists(db=db, name=smart_hardware_internal_dict["name"])
    if db_smart_hardware:
        raise DuplicateValueException("SmartHardware Name not available")

    smart_hardware_internal_dict["update_user"] = None
    smart_hardware_internal = SmartHardwareCreateInternal(**smart_hardware_internal_dict)
    created_smart_hardware = await crud_smart_hardwares.create(db=db, object=smart_hardware_internal)

    smart_hardware_read = await crud_smart_hardwares.get(db=db, id=created_smart_hardware.id, schema_to_select=SmartHardwareRead)
    if smart_hardware_read is None:
        raise NotFoundException("Created smart_hardware not found")

    return cast(SmartHardwareRead, smart_hardware_read)


# paginated response for smart_hardwares
@router.get("/smart-hardwares", response_model=PaginatedListResponse[SmartHardwareRead])
async def read_smart_hardwares(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    smart_hardwares_data = await crud_smart_hardwares.get_multi(db=db, offset=compute_offset(page, items_per_page), limit=items_per_page, is_deleted=False,)

    response: dict[str, Any] = paginated_response(crud_data=smart_hardwares_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/smart-hardware/{id}", response_model=SmartHardwareRead)
async def read_smart_hardware(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> SmartHardwareRead:
    db_smart_hardware = await crud_smart_hardwares.get(db=db, id=id, is_deleted=False, schema_to_select=SmartHardwareRead)
    if db_smart_hardware is None:
        raise NotFoundException("SmartHardware not found")

    return cast(SmartHardwareRead, db_smart_hardware)


@router.patch("/smart-hardware/{id}")
async def patch_smart_hardware(
    request: Request, id: int, values: SmartHardwareUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_smart_hardware = await crud_smart_hardwares.get(db=db, id=id, schema_to_select=SmartHardwareRead)
    if db_smart_hardware is None:
        raise NotFoundException("SmartHardware not found")

    existing_smart_hardware = await crud_smart_hardwares.exists(db=db, name=values.name)
    if existing_smart_hardware:
        raise DuplicateValueException("SmartHardware Name not available")

    await crud_smart_hardwares.update(db=db, object=values, id=id)
    return {"message": "SmartHardware updated"}


@router.delete("/smart-hardware/{id}")
async def erase_smart_hardware(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_smart_hardware = await crud_smart_hardwares.get(db=db, id=id, schema_to_select=SmartHardwareRead)
    if db_smart_hardware is None:
        raise NotFoundException("SmartHardware not found")

    await crud_smart_hardwares.delete(db=db, id=id)
    return {"message": "SmartHardware deleted"}


@router.get("/smart-hardwares/counts")
async def get_smart_hardware_counts(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, Any]:
    """Get smart hardware counts by status"""
    
    # Get all smart hardware devices that are not deleted
    smart_hardwares_data = await crud_smart_hardwares.get_multi(db=db, is_deleted=False)
    all_devices = smart_hardwares_data.get("data", [])
    
    # Initialize counters
    counts = {
        "online": 0,
        "offline": 0, 
        "all": len(all_devices),
        "un_bind": 0,
        "need_upgrade": 0
    }
    
    # Count devices by status and upgrade_status
    for device in all_devices:
        status = getattr(device, 'status', None)
        upgrade_status = getattr(device, 'upgrade_status', 0)
        
        # Count by connection status
        if status == "1":  # online
            counts["online"] += 1
        elif status == "2":  # offline
            counts["offline"] += 1
        elif status == "10":  # not-related/unbound
            counts["un_bind"] += 1
            
        # Count devices that need upgrade
        if upgrade_status == 1:
            counts["need_upgrade"] += 1
    
    return {
        "success": True,
        "data": counts
    }
