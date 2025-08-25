from fastcrud import FastCRUD

from ...models.permission.record import Record
from ...schemas.permission.record import RecordCreateInternal, RecordDelete, RecordRead, RecordUpdate, RecordUpdateInternal

CRUDRecord = FastCRUD[Record, RecordCreateInternal, RecordUpdate, RecordUpdateInternal, RecordDelete, RecordRead]
crud_records = CRUDRecord(Record)
