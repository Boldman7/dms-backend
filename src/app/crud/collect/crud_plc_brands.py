from fastcrud import FastCRUD

from ...models.plc_brand import PlcBrand
from ...schemas.plc_brand import PlcBrandCreateInternal, PlcBrandDelete, PlcBrandRead, PlcBrandUpdate, PlcBrandUpdateInternal

CRUDPlcBrand = FastCRUD[PlcBrand, PlcBrandCreateInternal, PlcBrandUpdate, PlcBrandUpdateInternal, PlcBrandDelete, PlcBrandRead]
crud_plc_brands = CRUDPlcBrand(PlcBrand)
