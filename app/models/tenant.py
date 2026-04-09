# Tenant, Subscription ORM models
import enum
import uuid

from sqlalchemy import UUID, Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PlanEnum(str, enum.Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    CANCELED = "canceled"
    PAST_DUE = "past_due"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))

    plan: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "basic", "pro", "enterprise"
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status_enum"),
        default=SubscriptionStatus.TRIAL,
    )
    start_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)

    tenant = relationship("Tenant", back_populates="subscriptions")


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    domain: Mapped[str] = mapped_column(
        String(60), unique=True, index=True, nullable=False
    )
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)

    # owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    billing_email: Mapped[str] = mapped_column(String(255), nullable=True)

    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    deleted_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # soft delete

    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="tenant"
    )
    users = relationship("Membership", back_populates="tenant")
