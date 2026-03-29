# User, Role, Permission
import enum
import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseMixin


class RoleEnum(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"


class Membership(Base, BaseMixin):
    __tablename__ = "memberships"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE")
    )
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"))

    user = relationship("User", back_populates="memberships")
    tenant = relationship("Tenant", back_populates="users")
    role = relationship("Role")

    __table_args__ = (
        Index("ix_memberships_user_id", "user_id"),
        Index("ix_memberships_tenant_id", "tenant_id"),
        Index("ix_memberships_role_id", "role_id"),
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant_membership"),
    )


class Role(Base, BaseMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50))  # admin, manager, custom
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )

    permissions = relationship("RolePermission", back_populates="role")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_role_name_per_tenant"),
        Index(
            "uq_global_roles_name",
            "name",
            unique=True,
            postgresql_where=(tenant_id.is_(None)),
        ),
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission")


class Permission(Base, BaseMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(
        String(100), unique=True
    )  # "create_user", "view_reports"
    description: Mapped[str] = mapped_column(String(255), nullable=True)


class User(Base, BaseMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String(255), nullable=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    memberships = relationship("Membership", back_populates="user")
