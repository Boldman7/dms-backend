from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.equipment.crud_products import crud_products
from ....schemas.equipment.product import ProductCreate, ProductCreateInternal, ProductRead, ProductUpdate

router = APIRouter(tags=["products"])


@router.post("/product", status_code=201)
async def write_product(
    request: Request, product: ProductCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> ProductRead:
    product_internal_dict = product.model_dump()
    db_product = await crud_products.exists(db=db, name=product_internal_dict["name"])
    if db_product:
        raise DuplicateValueException("Product Name not available")

    product_internal_dict["update_user"] = None
    product_internal = ProductCreateInternal(**product_internal_dict)
    created_product = await crud_products.create(db=db, object=product_internal)

    product_read = await crud_products.get(db=db, id=created_product.id, schema_to_select=ProductRead)
    if product_read is None:
        raise NotFoundException("Created product not found")

    return cast(ProductRead, product_read)


# paginated response for products
@router.get("/products", response_model=PaginatedListResponse[ProductRead])
async def read_products(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict:
    products_data = await crud_products.get_multi(db=db, offset=compute_offset(page, items_per_page), limit=items_per_page, is_deleted=False,)

    response: dict[str, Any] = paginated_response(crud_data=products_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/product/{id}", response_model=ProductRead)
async def read_product(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> ProductRead:
    db_product = await crud_products.get(db=db, id=id, is_deleted=False, schema_to_select=ProductRead)
    if db_product is None:
        raise NotFoundException("Product not found")

    return cast(ProductRead, db_product)


@router.patch("/product/{id}")
async def patch_product(
    request: Request, id: int, values: ProductUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_product = await crud_products.get(db=db, id=id, schema_to_select=ProductRead)
    if db_product is None:
        raise NotFoundException("Product not found")

    existing_product = await crud_products.exists(db=db, name=values.name)
    if existing_product:
        raise DuplicateValueException("Product Name not available")

    await crud_products.update(db=db, object=values, id=id)
    return {"message": "Product updated"}


@router.delete("/product/{id}")
async def erase_product(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_product = await crud_products.get(db=db, id=id, schema_to_select=ProductRead)
    if db_product is None:
        raise NotFoundException("Product not found")

    await crud_products.delete(db=db, id=id)
    return {"message": "Product deleted"}
