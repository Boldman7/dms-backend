from typing import Annotated, Any, cast, Optional

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row
from sqlalchemy.orm import selectinload

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.permission.crud_roles import crud_roles
from ....schemas.permission.role import RoleCreate, RoleCreateInternal, RoleRead, RoleReadJoined, RoleUpdate
from ....schemas.base.company import CompanyRead
from ....models.base.company import Company
from ....models.permission.resource import Resource
from ....models.permission.role import Role

router = APIRouter(tags=["roles"])


@router.post("/role", status_code=201)
async def write_role(
    request: Request, role: RoleCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    role_internal_dict = role.model_dump()
    db_role = await crud_roles.get(db=db, name=role_internal_dict["name"])
    if db_role:
        if db_role["is_deleted"]:
            await crud_roles.db_delete(db=db, id=db_role["id"])
        else:
            raise DuplicateValueException("Role Name not available")
        
    resources = role_internal_dict.pop("resources", [])
    role_internal_dict["update_user"] = None

    role_internal = RoleCreateInternal(**role_internal_dict)
    created_role = await crud_roles.create(db=db, object=role_internal)

    if created_role is None:
        raise NotFoundException("Created role not found")
    
    if resources:
        result = await db.execute(select(Resource).where(Resource.id.in_(resources)))
        resources = result.scalars().all()
        created_role.resources.extend(resources)
        await db.commit()

    return {"message": "Role created"}


# paginated response for roles
@router.get("/roles", response_model=PaginatedListResponse[RoleReadJoined])
async def read_roles(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query(""),
    page: int | None = Query(1),
    items_per_page: int | None = Query(10)
) -> dict:
    result = await db.execute(
        select(Role)
        .options(
            selectinload(Role.resources),   # eager load resources
            selectinload(Role.company)      # eager load company
        )
        .offset(compute_offset(page, items_per_page))
        .limit(items_per_page)
        .where(Role.is_deleted == False, Role.name.contains(name))
    )
    roles = result.scalars().all()

    roles_data = {}
    roles_data["data"] = roles
    roles_data["total_count"] = await crud_roles.count(db=db, is_deleted=False, name__contains=name)

    response: dict[str, Any] = paginated_response(crud_data=roles_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/role/{id}", response_model=RoleReadJoined)
async def read_role(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> RoleReadJoined:
    db_role = await crud_roles.get_joined(
        db=db,
        id=id,
        join_model=Company,
        join_schema_to_select=CompanyRead,
        nest_joins=True,
        schema_to_select=RoleReadJoined,
        is_deleted=False,
    )
    if db_role is None:
        raise NotFoundException("Role not found")

    return db_role


@router.patch("/role/{id}")
async def patch_role(
    request: Request, id: int, values: RoleUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_role = await db.get(Role, id)
    if db_role is None:
        raise NotFoundException("Role not found")

    if values.name and values.name != db_role.name:
        existing_role = await crud_roles.get(db=db, name=values.name)
        if existing_role:
            if existing_role["is_deleted"]:
                await crud_roles.db_delete(db=db, id=existing_role["id"])
            else:
                raise DuplicateValueException("Role Name not available")

    resources = values.resources
    del values.resources
    await crud_roles.update(db=db, object=values, id=id)
    db_role.resources.clear()  # Clear existing resources

    if resources:
        result = await db.execute(select(Resource).where(Resource.id.in_(resources)))
        resources = result.scalars().all()
        db_role.resources.extend(resources)
        await db.commit()
        # await db.refresh(db_role)

    return {"message": "Role updated"}


@router.delete("/role/{id}")
async def erase_role(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_role = await crud_roles.get(db=db, id=id, schema_to_select=RoleRead)
    if db_role is None:
        raise NotFoundException("Role not found")

    await crud_roles.delete(db=db, id=id)
    return {"message": "Role deleted"}
