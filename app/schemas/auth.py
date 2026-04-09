import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class TenantBase(BaseModel):
    name: str = Field(title="Name of the company or organization...")
    domain: str


class TenantPublic(TenantBase):

    model_config = ConfigDict(from_attributes=True)

    plan: str  # basic,pro,enterprise
    status: str  # trial,active,cancelled


class TenantPrivate(TenantPublic):
    id: uuid.UUID
    email: EmailStr


class Register(BaseModel):
    email: EmailStr
    password: str
    name: str = Field(title="Name of the company or organization")  # Acme Corp
    domain: str  # "acme" becomes the subdomain

    @field_validator("domain")
    @classmethod
    def domain_must_be_lowercase_alphanumeric(cls, v: str) -> str:
        import re

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Domain must be lowercase letters, numbers, and hyphens only"
            )
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str
