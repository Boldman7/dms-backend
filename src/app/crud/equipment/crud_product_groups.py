from fastcrud import FastCRUD

from ...models.product_group import ProductGroup
from ...schemas.product_group import ProductGroupCreateInternal, ProductGroupDelete, ProductGroupRead, ProductGroupUpdate, ProductGroupUpdateInternal

CRUDProductGroup = FastCRUD[ProductGroup, ProductGroupCreateInternal, ProductGroupUpdate, ProductGroupUpdateInternal, ProductGroupDelete, ProductGroupRead]
crud_product_groups = CRUDProductGroup(ProductGroup)
