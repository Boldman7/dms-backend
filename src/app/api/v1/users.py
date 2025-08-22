from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request, Query
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...core.security import blacklist_token, get_password_hash, oauth2_scheme
from ...crud.crud_users import crud_users
from ...schemas.user import UserCreate, UserCreateInternal, UserRead, UserReadJoined, UserUpdate
from ...models.permission.role import Role
from ...models.user import User

router = APIRouter(tags=["users"])


@router.post("/user", response_model=UserRead, status_code=201)
async def write_user(
    request: Request, user: UserCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> UserRead:
    user_internal_dict = user.model_dump()
    db_user = await crud_users.get(db=db, email=user_internal_dict["email"])
    if db_user:
        if db_user["is_deleted"]:
            await crud_users.db_delete(db=db, id=db_user["id"])
        else:
            raise DuplicateValueException("Email is already registered")
    
    db_user = await crud_users.get(db=db, name=user_internal_dict["name"])
    if db_user:
        if db_user["is_deleted"]:
            await crud_users.db_delete(db=db, id=db_user["id"])
        else:
            raise DuplicateValueException("User Name not available")

    roles = user_internal_dict.pop("roles", [])
    user_internal_dict["update_user"] = None
    user_internal_dict["hashed_password"] = get_password_hash(password=user_internal_dict["password"])
    del user_internal_dict["password"]

    user_internal = UserCreateInternal(**user_internal_dict)
    created_user = await crud_users.create(db=db, object=user_internal)

    if created_user is None:
        raise NotFoundException("Created user not found")
    
    if roles:
        result = await db.execute(select(Role).where(Role.id.in_(roles)))
        roles = result.scalars().all()
        created_user.roles.extend(roles)
        await db.commit()
        await db.refresh(created_user)
    
    created_user.roles = roles

    return cast(UserRead, created_user)


@router.get("/users", response_model=PaginatedListResponse[UserReadJoined])
async def read_users(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    name: str = Query(""),
    company_id: int | None = Query(None),
    page: int | None = Query(1),
    items_per_page: int | None = Query(10)
) -> dict:
    if company_id:
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.roles),
                selectinload(User.company)
            )
            .offset(compute_offset(page, items_per_page))
            .limit(items_per_page)
            .where(User.is_deleted == False, User.name.contains(name), User.company_id == company_id)
        )
        total_count = await crud_users.count(db=db, is_deleted=False, name__contains=name, company_id=company_id)
    else:
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.roles),
                selectinload(User.company)
            )
            .offset(compute_offset(page, items_per_page))
            .limit(items_per_page)
            .where(User.is_deleted == False, User.name.contains(name))
        )
        total_count = await crud_users.count(db=db, is_deleted=False, name__contains=name)

    users = result.scalars().all()

    users_data = {}
    users_data["data"] = users
    users_data["total_count"] = total_count

    response: dict[str, Any] = paginated_response(crud_data=users_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/user/me/", response_model=UserRead)
async def read_users_me(request: Request, current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return current_user


@router.get("/user/{username}", response_model=UserRead)
async def read_user(request: Request, username: str, db: Annotated[AsyncSession, Depends(async_get_db)]) -> UserRead:
    db_user = await crud_users.get(db=db, username=username, is_deleted=False, schema_to_select=UserRead)
    if db_user is None:
        raise NotFoundException("User not found")

    return cast(UserRead, db_user)


@router.patch("/user/{id}")
async def patch_user(
    request: Request,
    values: UserUpdate,
    id: int,
    # current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    db_user = await db.get(User, id)
    if db_user is None:
        raise NotFoundException("User not found")

    # db_user = cast(UserRead, db_user)
    # if db_user.username != current_user["username"]:
        # raise ForbiddenException()

    if values.name and values.name != db_user.name:
        existing_user = await crud_users.get(db=db, name=values.name)
        if existing_user:
            if existing_user["is_deleted"]:
                await crud_users.db_delete(db=db, id=existing_user["id"])
            else:
                raise DuplicateValueException("User Name not available")

    if values.email and values.email != db_user.email:
        existing_user = await crud_users.get(db=db, email=values.email)
        if existing_user:
            if existing_user["is_deleted"]:
                await crud_users.db_delete(db=db, id=existing_user["id"])
            else:
                raise DuplicateValueException("Email is already registered")

    roles = values.roles
    del values.roles
    await crud_users.update(db=db, object=values, id=id)
    db_user.roles.clear()  # Clear existing roles

    if roles:
        result = await db.execute(select(Role).where(Role.id.in_(roles)))
        roles = result.scalars().all()
        db_user.roles.extend(roles)
        await db.commit()
        # await db.refresh(db_user)

    return {"message": "User updated"}


@router.delete("/user/{id}")
async def erase_user(
    request: Request,
    id: int,
    # current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
    # token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    db_user = await db.get(User, id)
    if not db_user:
        raise NotFoundException("User not found")

    # if db_user.id != current_user["id"]:
        # raise ForbiddenException()

    db_user.roles.clear()  # Clear existing roles
    await crud_users.delete(db=db, id=id)
    # await blacklist_token(token=token, db=db)
    return {"message": "User deleted"}


# @router.delete("/db_user/{id}", dependencies=[Depends(get_current_superuser)])
@router.delete("/db_user/{id}")
async def erase_db_user(
    request: Request,
    id: int,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    db_user = await crud_users.exists(db=db, id=id)
    if not db_user:
        raise NotFoundException("User not found")

    await crud_users.db_delete(db=db, id=id)
    await blacklist_token(token=token, db=db)
    return {"message": "User deleted from the database"}
