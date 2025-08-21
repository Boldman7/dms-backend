from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.permission.crud_resources import crud_resources
from ....schemas.permission.resource import ResourceCreate, ResourceCreateInternal, ResourceRead, ResourceUpdate, ResourceTreeNode

router = APIRouter(tags=["resources"])


@router.post("/resource", status_code=201)
async def write_resource(
    request: Request, resource: ResourceCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> ResourceRead:
    resource_internal_dict = resource.model_dump()
    db_resource = await crud_resources.get(db=db, name=resource_internal_dict["name"])
    if db_resource:
        if db_resource["is_deleted"]:
            await crud_resources.db_delete(db=db, id=db_resource["id"])
        else:
            raise DuplicateValueException("Resource Name not available")

    resource_internal_dict["update_user"] = None
    resource_internal = ResourceCreateInternal(**resource_internal_dict)
    created_resource = await crud_resources.create(db=db, object=resource_internal)

    resource_read = await crud_resources.get(db=db, id=created_resource.id, schema_to_select=ResourceRead)
    if resource_read is None:
        raise NotFoundException("Created resource not found")

    return cast(ResourceRead, resource_read)


# unpaginated response for resources
@router.get("/resources", response_model=dict[str, List[ResourceRead]])
async def read_resources(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[ResourceRead]:
    resources_data = await crud_resources.get_multi(db=db, is_deleted=False)

    response: dict[str, List[ResourceRead]] = {"data": cast(List[ResourceRead], resources_data["data"])}
    return response


@router.get("/resource/{id}", response_model=ResourceRead)
async def read_resource(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> ResourceRead:
    db_resource = await crud_resources.get(db=db, id=id, is_deleted=False, schema_to_select=ResourceRead)
    if db_resource is None:
        raise NotFoundException("Resource not found")

    return cast(ResourceRead, db_resource)


@router.patch("/resource/{id}")
async def patch_resource(
    request: Request, id: int, values: ResourceUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_resource = await crud_resources.get(db=db, id=id, schema_to_select=ResourceRead)
    if db_resource is None:
        raise NotFoundException("Resource not found")
    
    if values.name and values.name != db_resource["name"]:
        existing_resource = await crud_resources.get(db=db, name=values.name)
        if existing_resource:
            if existing_resource["is_deleted"]:
                await crud_resources.db_delete(db=db, id=existing_resource["id"])
            else:
                raise DuplicateValueException("Resource Name not available")

    await crud_resources.update(db=db, object=values, id=id)
    return {"message": "Resource updated"}


@router.delete("/resource/{id}")
async def erase_resource(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_resource = await crud_resources.get(db=db, id=id, schema_to_select=ResourceRead)
    if db_resource is None:
        raise NotFoundException("Resource not found")

    await crud_resources.delete(db=db, id=id)
    return {"message": "Resource deleted"}


# Hierarchical tree structure for resources
@router.get("/resources/tree", response_model=dict[str, List[ResourceTreeNode]])
async def read_resources_tree(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[ResourceTreeNode]:
    """Get resources in a hierarchical tree structure"""
    
    # Get all resources
    resources_data = await crud_resources.get_multi(db=db, is_deleted=False)
    all_resources = resources_data.get("data", [])
    
    # Convert to ResourceTreeNode objects
    resource_nodes = {}
    for resource in all_resources:
        resource_nodes[resource["id"]] = ResourceTreeNode(
            id=resource["id"],
            name=resource["name"],
            parent_id=resource["parent_id"],
            update_user=resource["update_user"],
            created_at=resource["created_at"],
            updated_at=resource["updated_at"],
            children=[]
        )
    
    # Build the tree structure
    root_resources = []
    
    for resource_node in resource_nodes.values():
        if resource_node.parent_id is None:
            # This is a root resource
            root_resources.append(resource_node)
        else:
            # This is a child resource, add it to its parent
            parent = resource_nodes.get(resource_node.parent_id)
            if parent:
                parent.children.append(resource_node)
    
    response: dict[str, List[ResourceTreeNode]] = {"data": cast(List[ResourceTreeNode], root_resources)}
    return response
