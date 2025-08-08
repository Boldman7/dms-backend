from fastcrud import FastCRUD

from ...models.smart_hardware import SmartHardware
from ...schemas.smart_hardware import SmartHardwareCreateInternal, SmartHardwareDelete, SmartHardwareRead, SmartHardwareUpdate, SmartHardwareUpdateInternal

CRUDSmartHardware = FastCRUD[SmartHardware, SmartHardwareCreateInternal, SmartHardwareUpdate, SmartHardwareUpdateInternal, SmartHardwareDelete, SmartHardwareRead]
crud_smart_hardwares = CRUDSmartHardware(SmartHardware)
