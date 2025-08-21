from fastcrud import FastCRUD

from ...models.permission.resource import Resource
from ...schemas.permission.resource import ResourceCreateInternal, ResourceDelete, ResourceRead, ResourceUpdate, ResourceUpdateInternal

CRUDResource = FastCRUD[Resource, ResourceCreateInternal, ResourceUpdate, ResourceUpdateInternal, ResourceDelete, ResourceRead]
crud_resources = CRUDResource(Resource)
