from fastcrud import FastCRUD

from ...models.collect.connection import Connection
from ...schemas.collect.connection import ConnectionCreateInternal, ConnectionDelete, ConnectionRead, ConnectionUpdate, ConnectionUpdateInternal

CRUDConnection = FastCRUD[Connection, ConnectionCreateInternal, ConnectionUpdate, ConnectionUpdateInternal, ConnectionDelete, ConnectionRead]
crud_connections = CRUDConnection(Connection)
