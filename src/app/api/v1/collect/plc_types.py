from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_plc_types import crud_plc_types
from ....crud.collect.crud_plc_brands import crud_plc_brands
from ....schemas.collect.plc_type import PlcTypeCreate, PlcTypeCreateInternal, PlcTypeRead, PlcTypeUpdate
from ....schemas.collect.plc_brand import PlcTreeNode

router = APIRouter(tags=["plc_types"])


@router.post("/plc-type", status_code=201)
async def write_plc_type(
    request: Request, plc_type: PlcTypeCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> PlcTypeRead:
    plc_type_internal_dict = plc_type.model_dump()

    plc_type_internal_dict["update_user"] = None
    plc_type_internal = PlcTypeCreateInternal(**plc_type_internal_dict)
    created_plc_type = await crud_plc_types.create(db=db, object=plc_type_internal)

    plc_type_read = await crud_plc_types.get(db=db, id=created_plc_type.id, schema_to_select=PlcTypeRead)
    if plc_type_read is None:
        raise NotFoundException("Created plc_type not found")

    return cast(PlcTypeRead, plc_type_read)


# unpaginated response for plc_types
@router.get("/plc-types", response_model=dict[str, List[PlcTypeRead]])
async def read_plc_types(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[PlcTypeRead]:
    plc_types_data = await crud_plc_types.get_multi(db=db, is_deleted=False)

    response: dict[str, List[PlcTypeRead]] = {"data": cast(List[PlcTypeRead], plc_types_data["data"])}
    return response


@router.get("/plc-type/{id}", response_model=PlcTypeRead)
async def read_plc_type(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> PlcTypeRead:
    db_plc_type = await crud_plc_types.get(db=db, id=id, is_deleted=False, schema_to_select=PlcTypeRead)
    if db_plc_type is None:
        raise NotFoundException("PlcType not found")

    return cast(PlcTypeRead, db_plc_type)


@router.patch("/plc-type/{id}")
async def patch_plc_type(
    request: Request, id: int, values: PlcTypeUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_plc_type = await crud_plc_types.get(db=db, id=id, schema_to_select=PlcTypeRead)
    if db_plc_type is None:
        raise NotFoundException("PlcType not found")

    await crud_plc_types.update(db=db, object=values, id=id)
    return {"message": "PlcType updated"}


@router.delete("/plc-type/{id}")
async def erase_plc_type(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_plc_type = await crud_plc_types.get(db=db, id=id, schema_to_select=PlcTypeRead)
    if db_plc_type is None:
        raise NotFoundException("PlcType not found")

    await crud_plc_types.delete(db=db, id=id)
    return {"message": "PlcType deleted"}


# Hierarchical tree structure for companies
@router.get("/plc-types/tree", response_model=dict[str, List[PlcTreeNode]])
async def read_companies_tree(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[PlcTreeNode]:
    """Get companies in a hierarchical tree structure"""
    
    # Get all plc_brands and plc_types
    plc_brands_data = await crud_plc_brands.get_multi(db=db, is_deleted=False)
    all_plc_brands = plc_brands_data.get("data", [])
    plc_types_data = await crud_plc_types.get_multi(db=db, is_deleted=False)
    all_plc_types = plc_types_data.get("data", [])

    plc_tree = []

    for plc_brand in all_plc_brands:
        plc_tree_node: PlcTreeNode = PlcTreeNode(
            id=plc_brand["id"],
            name=plc_brand["name"],
            plc_type_list=[
                PlcTypeRead(
                    id=plc_type["id"],
                    name=plc_type["name"],
                    plc_brand_id=plc_type["plc_brand_id"],
                    interface_type=plc_type["interface_type"],
                    controller_id=plc_type["controller_id"],
                    controller_name=plc_type["controller_name"],
                    update_user=plc_type["update_user"],
                    created_at=plc_type["created_at"],
                    updated_at=plc_type["updated_at"]
                )
                for plc_type in all_plc_types if plc_type["plc_brand_id"] == plc_brand["id"]
            ],
            update_user=plc_brand["update_user"],
            created_at=plc_brand["created_at"],
            updated_at=plc_brand["updated_at"]
        )
        plc_tree.append(plc_tree_node)
    
    response: dict[str, List[PlcTreeNode]] = {"data": cast(List[PlcTreeNode], plc_tree)}
    return response
