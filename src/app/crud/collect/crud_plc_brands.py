from fastcrud import FastCRUD

from ...models.collect.plc_brand import PlcBrand
from ...schemas.collect.plc_brand import PlcBrandCreateInternal, PlcBrandDelete, PlcBrandRead, PlcBrandUpdate, PlcBrandUpdateInternal

CRUDPlcBrand = FastCRUD[PlcBrand, PlcBrandCreateInternal, PlcBrandUpdate, PlcBrandUpdateInternal, PlcBrandDelete, PlcBrandRead]
crud_plc_brands = CRUDPlcBrand(PlcBrand)
