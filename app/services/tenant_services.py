from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant


async def get_tenant_by_slug(session: AsyncSession, domain: str) -> Tenant | None:
    if not domain:
        return None

    result = await session.execute(select(Tenant).where(Tenant.domain == domain))
    tenant = result.scalar_one_or_none()
    return tenant
