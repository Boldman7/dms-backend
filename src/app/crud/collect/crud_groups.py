from fastcrud import FastCRUD

from ...models.collect.group import Group
from ...schemas.collect.group import GroupCreateInternal, GroupDelete, GroupRead, GroupUpdate, GroupUpdateInternal

CRUDGroup = FastCRUD[Group, GroupCreateInternal, GroupUpdate, GroupUpdateInternal, GroupDelete, GroupRead]
crud_groups = CRUDGroup(Group)
