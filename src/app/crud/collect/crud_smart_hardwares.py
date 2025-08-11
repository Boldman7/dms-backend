from fastcrud import FastCRUD

from ...models.collect.smart_hardware import SmartHardware
from ...schemas.collect.smart_hardware import SmartHardwareCreateInternal, SmartHardwareDelete, SmartHardwareRead, SmartHardwareUpdate, SmartHardwareUpdateInternal

CRUDSmartHardware = FastCRUD[SmartHardware, SmartHardwareCreateInternal, SmartHardwareUpdate, SmartHardwareUpdateInternal, SmartHardwareDelete, SmartHardwareRead]
crud_smart_hardwares = CRUDSmartHardware(SmartHardware)
