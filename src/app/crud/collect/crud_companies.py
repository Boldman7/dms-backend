from fastcrud import FastCRUD

from ...models.company import Company
from ...schemas.company import CompanyCreateInternal, CompanyDelete, CompanyRead, CompanyUpdate, CompanyUpdateInternal

CRUDCompany = FastCRUD[Company, CompanyCreateInternal, CompanyUpdate, CompanyUpdateInternal, CompanyDelete, CompanyRead]
crud_companies = CRUDCompany(Company)
