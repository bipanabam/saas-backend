from contextvars import ContextVar
from uuid import UUID

# Define the ContextVar
_current_tenant_id: ContextVar[UUID | None] = ContextVar(
    "_current_tenant_id", default=None
)


def get_current_tenant_id() -> UUID | None:
    """Get the current tenant ID from the context."""
    tenant_id = _current_tenant_id.get()
    if tenant_id is None:
        raise RuntimeError("No tenant ID set in the current context.")
    return tenant_id


def set_current_tenant_id(tenant_id: UUID) -> None:
    """Set the current tenant ID in the context."""
    _current_tenant_id.set(tenant_id)
