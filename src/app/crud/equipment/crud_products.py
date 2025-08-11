from fastcrud import FastCRUD

from ...models.equipment.product import Product
from ...schemas.equipment.product import ProductCreateInternal, ProductDelete, ProductRead, ProductUpdate, ProductUpdateInternal

CRUDProduct = FastCRUD[Product, ProductCreateInternal, ProductUpdate, ProductUpdateInternal, ProductDelete, ProductRead]
crud_products = CRUDProduct(Product)
