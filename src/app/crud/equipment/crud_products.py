from fastcrud import FastCRUD

from ...models.product import Product
from ...schemas.product import ProductCreateInternal, ProductDelete, ProductRead, ProductUpdate, ProductUpdateInternal

CRUDProduct = FastCRUD[Product, ProductCreateInternal, ProductUpdate, ProductUpdateInternal, ProductDelete, ProductRead]
crud_products = CRUDProduct(Product)
