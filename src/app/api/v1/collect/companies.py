from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.collect.crud_companies import crud_companies
from ....schemas.company import CompanyCreate, CompanyCreateInternal, CompanyRead, CompanyUpdate, CompanyTreeNode

router = APIRouter(tags=["companies"])


@router.post("/company", status_code=201)
async def write_company(
    request: Request, company: CompanyCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> CompanyRead:
    company_internal_dict = company.model_dump()
    db_company = await crud_companies.exists(db=db, name=company_internal_dict["name"])
    if db_company:
        raise DuplicateValueException("Company Name not available")

    company_internal_dict["update_user"] = None
    company_internal = CompanyCreateInternal(**company_internal_dict)
    created_company = await crud_companies.create(db=db, object=company_internal)

    company_read = await crud_companies.get(db=db, id=created_company.id, schema_to_select=CompanyRead)
    if company_read is None:
        raise NotFoundException("Created company not found")

    return cast(CompanyRead, company_read)


@router.get("/companies", response_model=List[CompanyRead])
async def read_companies(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[CompanyRead]:
    companies_data = await crud_companies.get_multi(db=db, is_deleted=False)

    return cast(List[CompanyRead], companies_data["data"])


@router.get("/company/{id}", response_model=CompanyRead)
async def read_company(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> CompanyRead:
    db_company = await crud_companies.get(db=db, id=id, is_deleted=False, schema_to_select=CompanyRead)
    if db_company is None:
        raise NotFoundException("Company not found")

    return cast(CompanyRead, db_company)


@router.patch("/company/{id}")
async def patch_company(
    request: Request, id: int, values: CompanyUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_company = await crud_companies.get(db=db, id=id, schema_to_select=CompanyRead)
    if db_company is None:
        raise NotFoundException("Company not found")

    existing_company = await crud_companies.exists(db=db, name=values.name)
    if existing_company:
        raise DuplicateValueException("Company Name not available")

    await crud_companies.update(db=db, object=values, id=id)
    return {"message": "Company updated"}


@router.delete("/company/{id}")
async def erase_company(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_company = await crud_companies.get(db=db, id=id, schema_to_select=CompanyRead)
    if db_company is None:
        raise NotFoundException("Company not found")

    await crud_companies.delete(db=db, id=id)
    return {"message": "Company deleted"}


@router.get("/companies/tree", response_model=List[CompanyTreeNode])
async def read_companies_tree(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[CompanyTreeNode]:
    """Get companies in a hierarchical tree structure"""
    
    # Get all companies
    companies_data = await crud_companies.get_multi(db=db, is_deleted=False)
    all_companies = companies_data.get("data", [])
    
    # Convert to CompanyTreeNode objects
    company_nodes = {}
    for company in all_companies:
        company_nodes[company.id] = CompanyTreeNode(
            id=company.id,
            name=company.name,
            parent_id=company.parent_id,
            province=company.province,
            city=company.city,
            area=company.area,
            address=company.address,
            email=company.email,
            officePhone=company.officePhone,
            isEndUser=company.isEndUser,
            update_user=company.update_user,
            created_at=company.created_at,
            updated_at=company.updated_at,
            children=[]
        )
    
    # Build the tree structure
    root_companies = []
    
    for company_node in company_nodes.values():
        if company_node.parent_id is None:
            # This is a root company
            root_companies.append(company_node)
        else:
            # This is a child company, add it to its parent
            parent = company_nodes.get(company_node.parent_id)
            if parent:
                parent.children.append(company_node)
    
    return root_companies
