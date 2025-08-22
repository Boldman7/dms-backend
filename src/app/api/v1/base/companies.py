from typing import Annotated, List, cast, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Row, select
from sqlalchemy.orm import selectinload

from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import NotFoundException
from ....crud.base.crud_companies import crud_companies
from ....schemas.base.company import CompanyCreate, CompanyCreateInternal, CompanyRead, CompanyReadJoined, CompanyUpdate, CompanyTreeNode
from ....models.base.company import Company
from ....models.permission.resource import Resource

router = APIRouter(tags=["companies"])


@router.post("/company", status_code=201)
async def write_company(
    request: Request, company: CompanyCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> CompanyRead:
    company_internal_dict = company.model_dump()

    resources = company_internal_dict.pop("resources", [])
    company_internal_dict["update_user"] = None

    company_internal = CompanyCreateInternal(**company_internal_dict)
    created_company = await crud_companies.create(db=db, object=company_internal)

    if created_company is None:
        raise NotFoundException("Created company not found")
    
    if resources:
        result = await db.execute(select(Resource).where(Resource.id.in_(resources)))
        resources = result.scalars().all()
        created_company.resources.extend(resources)
        await db.commit()
        await db.refresh(created_company)

    created_company.resources = resources

    return cast(CompanyRead, created_company)


# unpaginated response for companies
@router.get("/companies", response_model=dict[str, List[CompanyRead]])
async def read_companies(
    request: Request, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> List[CompanyRead]:
    companies_data = await crud_companies.get_multi(db=db, is_deleted=False)

    response: dict[str, List[CompanyRead]] = {"data": cast(List[CompanyRead], companies_data["data"])}
    return response


@router.get("/company/{id}", response_model=CompanyReadJoined)
async def read_company(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> CompanyReadJoined:
    result = await db.execute(
        select(Company)
        .options(selectinload(Company.resources))   # <-- eager load roles
        .where(Company.is_deleted == False, Company.id == id)
    )
    company: Optional[Row] = result.scalars().first()

    if company is None:
        raise NotFoundException("Company not found")

    return cast(CompanyReadJoined, company)


@router.patch("/company/{id}")
async def patch_company(
    request: Request, id: int, values: CompanyUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    db_company = await db.get(Company, id)
    if db_company is None:
        raise NotFoundException("Company not found")

    resources = values.resources
    del values.resources
    await crud_companies.update(db=db, object=values, id=id)
    db_company.resources.clear()  # Clear existing resources

    if resources:
        result = await db.execute(select(Resource).where(Resource.id.in_(resources)))
        resources = result.scalars().all()
        db_company.resources.extend(resources)
        await db.commit()
        # await db.refresh(db_company)

    return {"message": "Company updated"}


@router.delete("/company/{id}")
async def erase_company(request: Request, id: int, db: Annotated[AsyncSession, Depends(async_get_db)]) -> dict[str, str]:
    db_company = await crud_companies.get(db=db, id=id, schema_to_select=CompanyRead)
    if db_company is None:
        raise NotFoundException("Company not found")

    await crud_companies.delete(db=db, id=id)
    return {"message": "Company deleted"}


# Hierarchical tree structure for companies
@router.get("/companies/tree", response_model=dict[str, List[CompanyTreeNode]])
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
        company_nodes[company["id"]] = CompanyTreeNode(
            id=company["id"],
            name=company["name"],
            parent_id=company["parent_id"],
            province=company["province"],
            city=company["city"],
            area=company["area"],
            address=company["address"],
            email=company["email"],
            phone_number=company["phone_number"],
            is_end_user=company["is_end_user"],
            update_user=company["update_user"],
            created_at=company["created_at"],
            updated_at=company["updated_at"],
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
    
    response: dict[str, List[CompanyTreeNode]] = {"data": cast(List[CompanyTreeNode], root_companies)}
    return response
