from fastapi import APIRouter, HTTPException
from sqlmodel import select
from database.engine import SessionDep
from database.models.tenant import Tenant, TenantPublic

router = APIRouter()


@router.get("/tenants/", tags=["Tenants"], response_model=list[TenantPublic])
async def read_tenants(session: SessionDep = SessionDep):
    tenants = session.exec(select(Tenant)).all()

    return tenants


@router.get("/tenants/{tenant_id}", tags=["Tenants"], response_model=TenantPublic)
async def read_tenant(tenant_id: int, session: SessionDep = SessionDep):
    print(f"Fetching tenant with ID: {tenant_id}, type of tenant_id: {type(tenant_id)}")
    tenant = session.exec(select(Tenant).where(Tenant.id == tenant_id)).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    return tenant
