from fastcrud import FastCRUD

from ...models.collect.company import Company
from ...schemas.collect.company import CompanyCreateInternal, CompanyDelete, CompanyRead, CompanyUpdate, CompanyUpdateInternal

CRUDCompany = FastCRUD[Company, CompanyCreateInternal, CompanyUpdate, CompanyUpdateInternal, CompanyDelete, CompanyRead]
crud_companies = CRUDCompany(Company)
