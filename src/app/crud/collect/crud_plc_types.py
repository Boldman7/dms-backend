from fastcrud import FastCRUD

from ...models.collect.plc_type import PlcType
from ...schemas.collect.plc_type import PlcTypeCreateInternal, PlcTypeDelete, PlcTypeRead, PlcTypeUpdate, PlcTypeUpdateInternal

CRUDPlcType = FastCRUD[PlcType, PlcTypeCreateInternal, PlcTypeUpdate, PlcTypeUpdateInternal, PlcTypeDelete, PlcTypeRead]
crud_plc_types = CRUDPlcType(PlcType)
