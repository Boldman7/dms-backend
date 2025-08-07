from fastcrud import FastCRUD

from ...models.plc_type import PlcType
from ...schemas.plc_type import PlcTypeCreateInternal, PlcTypeDelete, PlcTypeRead, PlcTypeUpdate, PlcTypeUpdateInternal

CRUDPlcType = FastCRUD[PlcType, PlcTypeCreateInternal, PlcTypeUpdate, PlcTypeUpdateInternal, PlcTypeDelete, PlcTypeRead]
crud_plc_types = CRUDPlcType(PlcType)
