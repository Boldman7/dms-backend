from fastcrud import FastCRUD

from ...models.data_source import DataSource
from ...schemas.data_source import DataSourceCreateInternal, DataSourceDelete, DataSourceRead, DataSourceUpdate, DataSourceUpdateInternal

CRUDDataSource = FastCRUD[DataSource, DataSourceCreateInternal, DataSourceUpdate, DataSourceUpdateInternal, DataSourceDelete, DataSourceRead]
crud_data_sources = CRUDDataSource(DataSource)
