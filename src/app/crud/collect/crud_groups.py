from fastcrud import FastCRUD

from ...models.group import Group
from ...schemas.group import GroupCreateInternal, GroupDelete, GroupRead, GroupUpdate, GroupUpdateInternal

CRUDGroup = FastCRUD[Group, GroupCreateInternal, GroupUpdate, GroupUpdateInternal, GroupDelete, GroupRead]
crud_groups = CRUDGroup(Group)
