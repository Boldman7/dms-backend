from fastcrud import FastCRUD

from ...models.equipment.data_source import DataSource
from ...schemas.equipment.data_source import DataSourceCreateInternal, DataSourceDelete, DataSourceRead, DataSourceUpdate, DataSourceUpdateInternal

CRUDDataSource = FastCRUD[DataSource, DataSourceCreateInternal, DataSourceUpdate, DataSourceUpdateInternal, DataSourceDelete, DataSourceRead]
crud_data_sources = CRUDDataSource(DataSource)
