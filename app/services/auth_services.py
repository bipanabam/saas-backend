from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import Subscription, SubscriptionStatus, Tenant, User
from app.schemas.auth import Register


class EmailAlreadyExistsError(Exception): ...


class DomainAlreadyExistsError(Exception): ...


async def register(
    payload: Register, db: AsyncSession
) -> tuple[Tenant, Subscription, User]:
    """ "Creates tenant and owner user automatically"""
    result = await db.execute(select(Tenant).where(Tenant.domain == payload.domain))

    existing_tenant = result.scalar_one_or_none()
    if existing_tenant:
        raise DomainAlreadyExistsError(f"Domain '{payload.domain}' already exists")

    result = await db.execute(select(User).where(User.email == payload.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise EmailAlreadyExistsError("Email already exists")

    tenant = Tenant(name=payload.name, domain=payload.domain, is_active=True)
    db.add(tenant)
    await db.flush()

    subscription_end_date = datetime.now(UTC) + timedelta(days=14)
    subscription = Subscription(
        tenant_id=tenant.id,
        plan="basic",
        status=SubscriptionStatus.TRIAL,
        start_date=datetime.now(UTC),
        end_date=subscription_end_date,
        auto_renew=False,
    )
    db.add(subscription)
    await db.flush()

    tenant_owner = User(
        email=payload.email,
        username=payload.email.split("@")[0],
        hashed_password=hash_password(payload.password),
    )
    db.add(tenant_owner)
    await db.flush()

    # result = await db.execute(
    #     select(Role).where(Role.name=="owner")
    # )
    # owner_role = result.scalar_one_or_none()
    # membership = Membership(
    #     user_id=tenant_owner.id,
    #     tenant_id=tenant.id,
    #     role_id=owner_role.id
    # )
    # db.add(membership)
    # await db.flush()

    return tenant, subscription, tenant_owner  # service never commits directly
