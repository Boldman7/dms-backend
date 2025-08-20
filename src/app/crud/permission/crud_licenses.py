from fastcrud import FastCRUD

from ...models.permission.license import License
from ...schemas.permission.license import LicenseCreateInternal, LicenseDelete, LicenseRead, LicenseUpdate, LicenseUpdateInternal

CRUDLicense = FastCRUD[License, LicenseCreateInternal, LicenseUpdate, LicenseUpdateInternal, LicenseDelete, LicenseRead]
crud_licenses = CRUDLicense(License)
