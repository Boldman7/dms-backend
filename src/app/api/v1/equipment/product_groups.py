from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.equipment.crud_product_groups import crud_product_groups
from ....schemas.equipment.product_group import ProductGroupCreate, ProductGroupCreateInternal, ProductGroupRead, ProductGroupUpdate, ProductGroupTreeNode

router = APIRouter(tags=["product_groups"])


@router.post("/product-group", status_code=201)
async def write_product_group(
    request: Request, product_group: ProductGroupCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> ProductGroupRead:
    product_group_internal_dict = product_group.model_dump()
    db_product_group = await crud_product_groups.get(db=db, name=product_group_internal_dict["name"])
    if db_product_group:
        if db_product_group["is_deleted"]:
            await crud_product_groups.db_delete(db=db, id=db_product_group["id"])
        else:
            raise DuplicateValueException("ProductGroup Name not available")

    product_group_internal_dict["update_user"] = None
    product_group_internal = ProductGroupCreateInternal(**product_group_internal_dict)
    created_product_group = await crud_product_groups.create(db=db, object=product_group_internal)

    product_group_read = await crud_product_groups.get(db=db, id=created_product_group.id, schema_to_select=ProductGroupRead)
    if product_group_read is None:
        raise NotFoundException("Created product_group not found")

    return cast(ProductGroupRead, product_group_read)


# unpaginated response for product_groups
@router.get("/product-groups", response_model=List[ProductGroupRead])
async def read_product_groups(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[ProductGroupRead]:
    product_groups_data = await crud_product_groups.get_multi(db=db, is_deleted=False)

    return cast(List[ProductGroupRead], product_groups_data["data"])


@router.get("/product-group/{id}", response_model=ProductGroupRead)
async def read_product_group(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> ProductGroupRead:
    db_product_group = await crud_product_groups.get(db=db, id=id, is_deleted=False, schema_to_select=ProductGroupRead)
    if db_product_group is None:
        raise NotFoundException("ProductGroup not found")

    return cast(ProductGroupRead, db_product_group)


@router.patch("/product-group/{id}")
async def patch_product_group(
    request: Request, id: int, values: ProductGroupUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_product_group = await crud_product_groups.get(db=db, id=id, schema_to_select=ProductGroupRead)
    if db_product_group is None:
        raise NotFoundException("ProductGroup not found")

    if values.name and values.name != db_product_group["name"]:
        existing_product_group = await crud_product_groups.get(db=db, name=values.name)
        if existing_product_group:
            if existing_product_group["is_deleted"]:
                await crud_product_groups.db_delete(db=db, id=existing_product_group["id"])
            else:
                raise DuplicateValueException("ProductGroup Name not available")

    await crud_product_groups.update(db=db, object=values, id=id)
    return {"message": "ProductGroup updated"}


@router.delete("/product-group/{id}")
async def erase_product_group(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_product_group = await crud_product_groups.get(db=db, id=id, schema_to_select=ProductGroupRead)
    if db_product_group is None:
        raise NotFoundException("ProductGroup not found")

    await crud_product_groups.delete(db=db, id=id)
    return {"message": "ProductGroup deleted"}


# Hierarchical tree structure for product_groups
@router.get("/product-groups/tree", response_model=dict[str, List[ProductGroupTreeNode]])
async def read_product_groups_tree(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[ProductGroupTreeNode]:
    """Get product_groups in a hierarchical tree structure"""
    
    # Get all product_groups
    product_groups_data = await crud_product_groups.get_multi(db=db, is_deleted=False)
    all_product_groups = product_groups_data.get("data", [])
    
    # Convert to ProductGroupTreeNode objects
    product_group_nodes = {}
    for product_group in all_product_groups:
        product_group_nodes[product_group["id"]] = ProductGroupTreeNode(
            id=product_group["id"],
            name=product_group["name"],
            parent_id=product_group["parent_id"],
            update_user=product_group["update_user"],
            created_at=product_group["created_at"],
            updated_at=product_group["updated_at"],
            children=[]
        )
    
    # Build the tree structure
    root_product_groups = []
    
    for product_group_node in product_group_nodes.values():
        if product_group_node.parent_id is None:
            # This is a root product_group
            root_product_groups.append(product_group_node)
        else:
            # This is a child product_group, add it to its parent
            parent = product_group_nodes.get(product_group_node.parent_id)
            if parent:
                parent.children.append(product_group_node)
    
    response: dict[str, List[ProductGroupTreeNode]] = {"data": cast(List[ProductGroupTreeNode], root_product_groups)}
    return response
