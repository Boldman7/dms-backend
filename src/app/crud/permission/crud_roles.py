from fastcrud import FastCRUD

from ...models.permission.role import Role
from ...schemas.permission.role import RoleCreateInternal, RoleDelete, RoleRead, RoleUpdate, RoleUpdateInternal

CRUDRole = FastCRUD[Role, RoleCreateInternal, RoleUpdate, RoleUpdateInternal, RoleDelete, RoleRead]
crud_roles = CRUDRole(Role)
