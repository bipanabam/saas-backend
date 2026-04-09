# import asyncio
# from collections.abc import AsyncGenerator
# from uuid import uuid4

# import pytest
# import pytest_asyncio
# from httpx import ASGITransport, AsyncClient
# from sqlalchemy import event
# from sqlalchemy.ext.asyncio import (
#     AsyncConnection,
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine,
# )

# from app.core.database import Base
# from app.core.security import create_access_token, get_password_hash
# from app.main import app
# from app.models.tenant import Tenant
# from app.models.user import User

# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# @pytest.fixture(scope="session")
# def event_loop():
#     """Single event loop for the whole test session (required by pytest-asyncio)."""
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


# @pytest_asyncio.fixture(scope="session")
# async def engine():
#     """
#     Create a test engine. Drops all tables and recreates them fresh at the
#     start of each test session so we always start from a clean slate.
#     """
#     test_engine = create_async_engine(
#         TEST_DATABASE_URL,
#         echo=False,  # set True to see SQL during debugging
#         pool_pre_ping=True,
#     )

#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)

#     yield test_engine

#     # Tear down after the full session
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

#     await test_engine.dispose()


# @event.listens_for(AsyncSession, "after_transaction_end")
# def restart_savepoint(session, transaction):
#     if transaction.nested and not transaction._parent.nested:
#         session.begin_nested()


# @pytest_asyncio.fixture()
# async def connection(engine) -> AsyncGenerator[AsyncConnection, None]:
#     """
#     A single AsyncConnection whose transaction is rolled back after each test.
#     """
#     async with engine.connect() as conn:
#         await conn.begin()  # outer transaction
#         await conn.begin_nested()  # SAVEPOINT

#         yield conn

#         await conn.rollback()  # rolls back outer → DB unchanged


# @pytest_asyncio.fixture()
# async def db(connection, monkeypatch) -> AsyncGenerator[AsyncSession, None]:
#     """
#     An AsyncSession bound to the test connection.
#     Automatically injected into any fixture or test that declares it.

#     Also patches async_session_factory in app so that FastAPI
#     dependency-injected sessions use this same rolled-back connection.
#     """
#     test_session_factory = async_sessionmaker(
#         bind=connection,
#         class_=AsyncSession,
#         expire_on_commit=False,
#         autoflush=False,
#         autocommit=False,
#     )

#     # Patch the factory your middleware and services import
#     import app.core.database as db_module

#     monkeypatch.setattr(db_module, "async_session_factory", test_session_factory)

#     async with test_session_factory() as session:
#         yield session


# @pytest_asyncio.fixture()
# async def tenant_a(db: AsyncSession) -> Tenant:
#     """Tenant A — 'acme', Pro plan."""
#     tenant = Tenant(
#         id=uuid4(),
#         name="Acme Corp",
#         slug="acme",
#         plan="pro",
#         is_active=True,
#         stripe_customer_id="cus_test_acme",  # remove if not on your model yet
#     )
#     db.add(tenant)
#     await db.flush()  # flush → gets DB-generated fields; no commit needed
#     return tenant


# @pytest_asyncio.fixture()
# async def tenant_b(db: AsyncSession) -> Tenant:
#     """Tenant B — 'globex', Free plan."""
#     tenant = Tenant(
#         id=uuid4(),
#         name="Globex Inc",
#         slug="globex",
#         plan="free",
#         is_active=True,
#         stripe_customer_id="cus_test_globex",
#     )
#     db.add(tenant)
#     await db.flush()
#     return tenant


# # TEST USERS — one owner per tenant
# @pytest_asyncio.fixture()
# async def user_a(db: AsyncSession, tenant_a: Tenant) -> User:
#     """Owner user belonging to tenant_a."""
#     user = User(
#         id=uuid4(),
#         tenant_id=tenant_a.id,
#         email="owner@acme.com",
#         hashed_password=get_password_hash("testpassword"),
#         role="owner",
#         is_active=True,
#     )
#     db.add(user)
#     await db.flush()
#     return user


# @pytest_asyncio.fixture()
# async def user_b(db: AsyncSession, tenant_b: Tenant) -> User:
#     """Owner user belonging to tenant_b."""
#     user = User(
#         id=uuid4(),
#         tenant_id=tenant_b.id,
#         email="owner@globex.com",
#         hashed_password=get_password_hash("testpassword"),
#         role="owner",
#         is_active=True,
#     )
#     db.add(user)
#     await db.flush()
#     return user


# @pytest.fixture()
# def auth_headers_a(user_a: User, tenant_a: Tenant) -> dict[str, str]:
#     """JWT headers for user_a (tenant acme)."""
#     token = create_access_token(
#         data={
#             "sub": str(user_a.id),
#             "tenant_id": str(tenant_a.id),
#             "tenant_slug": tenant_a.slug,
#             "role": user_a.role,
#         }
#     )
#     return {"Authorization": f"Bearer {token}"}


# @pytest.fixture()
# def auth_headers_b(user_b: User, tenant_b: Tenant) -> dict[str, str]:
#     """JWT headers for user_b (tenant globex)."""
#     token = create_access_token(
#         data={
#             "sub": str(user_b.id),
#             "tenant_id": str(tenant_b.id),
#             "tenant_slug": tenant_b.slug,
#             "role": user_b.role,
#         }
#     )
#     return {"Authorization": f"Bearer {token}"}


# @pytest_asyncio.fixture()
# async def client_a(tenant_a: Tenant) -> AsyncGenerator[AsyncClient, None]:
#     """
#     HTTP client pre-configured for tenant_a (acme).
#     Host header → TenantResolverMiddleware picks up slug 'acme'.
#     """
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://acme.testserver",
#         headers={"host": "acme.testserver"},
#     ) as client:
#         yield client


# @pytest_asyncio.fixture()
# async def client_b(tenant_b: Tenant) -> AsyncGenerator[AsyncClient, None]:
#     """
#     HTTP client pre-configured for tenant_b (globex).
#     """
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://globex.testserver",
#         headers={"host": "globex.testserver"},
#     ) as client:
#         yield client


# from app.core.tenant_context import _current_tenant_id as _tenant_id_ctx_var


# @pytest.fixture()
# def with_tenant_a(tenant_a: Tenant):
#     """Set tenant_a as the active tenant context for direct service calls."""
#     token = _tenant_id_ctx_var.set(tenant_a.id)
#     yield tenant_a
#     _tenant_id_ctx_var.reset(token)


# @pytest.fixture()
# def with_tenant_b(tenant_b: Tenant):
#     """Set tenant_b as the active tenant context for direct service calls."""
#     token = _tenant_id_ctx_var.set(tenant_b.id)
#     yield tenant_b
#     _tenant_id_ctx_var.reset(token)
