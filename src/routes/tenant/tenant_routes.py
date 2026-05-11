from fastapi import APIRouter, HTTPException
from sqlmodel import select
from database.engine import SessionDep
from database.models.tenant import Tenant, TenantPublic

router = APIRouter()


@router.get("/tenants/", tags=["Tenants"], response_model=list[TenantPublic])
async def read_tenants(session: SessionDep = SessionDep):
    tenants = session.exec(select(Tenant)).all()

    return tenants


@router.get(
    "/tenants/subdomain/{tenant_subdomain}",
    tags=["Tenants"],
    response_model=TenantPublic,
)
async def read_tenant(tenant_subdomain: str, session: SessionDep = SessionDep):
    print(f"Fetching tenant with subdomain: {tenant_subdomain}")
    tenant = session.exec(
        select(Tenant).where(Tenant.subdomain == tenant_subdomain)
    ).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    return tenant


@router.get("/tenants/{tenant_id}", tags=["Tenants"], response_model=TenantPublic)
async def read_tenant(tenant_id: str, session: SessionDep = SessionDep):
    print(f"\n\n\n\nFetching tenant with ID: {tenant_id}")
    tenant = session.exec(select(Tenant).where(Tenant.id == tenant_id)).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    return tenant
