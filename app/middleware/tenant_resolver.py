from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.database import async_session_factory
from app.core.tenant_context import set_current_tenant_id
from app.services.tenant_services import get_tenant_by_slug


class TenantResolverMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # 1. Extract from subdomain (e.g., tenant1.example.com)
        host = request.headers.get("host", "")
        slug = host.split(".")[0]

        # 2. JWT claim (for mobile/API clients without subdomains)
        # slug = request.state.jwt_claims.get("tenant_slug")

        async with async_session_factory() as session:
            tenant = await get_tenant_by_slug(session, slug)

        if not tenant or not tenant.is_active:
            return Response("Tenant not found", status_code=404)

        set_current_tenant_id(tenant.id)
        return await call_next(request)
