from fastcrud import FastCRUD

from ...models.base.company import Company
from ...schemas.base.company import CompanyCreateInternal, CompanyDelete, CompanyRead, CompanyUpdate, CompanyUpdateInternal

CRUDCompany = FastCRUD[Company, CompanyCreateInternal, CompanyUpdate, CompanyUpdateInternal, CompanyDelete, CompanyRead]
crud_companies = CRUDCompany(Company)
