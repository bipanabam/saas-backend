# /register, /login, /logout, /refresh
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import Register, TenantPublic
from app.services.auth_services import (
    DomainAlreadyExistsError,
    EmailAlreadyExistsError,
    register,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# Register a new tenant and admin user
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_tenant(
    payload: Register, db: Annotated[AsyncSession, Depends(get_db)]
) -> TenantPublic:
    try:
        tenant, subscription, tenant_owner = await register(db=db, payload=payload)
        await db.commit()
    except DomainAlreadyExistsError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except EmailAlreadyExistsError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e

    return TenantPublic(
        name=tenant.name,
        domain=tenant.domain,
        plan=subscription.plan,
        status=subscription.status,
    )
