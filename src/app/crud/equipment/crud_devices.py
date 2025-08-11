from fastcrud import FastCRUD

from ...models.equipment.device import Device
from ...schemas.equipment.device import DeviceCreateInternal, DeviceDelete, DeviceRead, DeviceUpdate, DeviceUpdateInternal

CRUDDevice = FastCRUD[Device, DeviceCreateInternal, DeviceUpdate, DeviceUpdateInternal, DeviceDelete, DeviceRead]
crud_devices = CRUDDevice(Device)
