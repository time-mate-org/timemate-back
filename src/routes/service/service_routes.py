from fastapi import APIRouter, HTTPException, Request
from sqlmodel import select
from database.models.service import Service, ServicePublic
from database.engine import SessionDep
from utils import get_service_by_id, select_by_tenant_id
from validations import service_validation

router = APIRouter()


@router.get("/services/", tags=["Services"], response_model=list[ServicePublic])
async def read_services(request: Request, session: SessionDep = SessionDep):
    services = select_by_tenant_id(session, Service, tenant_id=request.state.tenant_id)

    return services


@router.get("/services/{service_id}", tags=["Services"], response_model=ServicePublic)
async def read_service(
    request: Request, service_id: int, session: SessionDep = SessionDep
):

    service = get_service_by_id(session, service_id, tenant_id=request.state.tenant_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    return service


@router.post(
    "/services/create/",
    tags=["Services"],
    status_code=201,
    response_model=ServicePublic,
)
async def create_service(
    request: Request,
    service: service_validation.ServiceCreateValidation,
    session: SessionDep = SessionDep,
):
    services = select_by_tenant_id(
        session,
        Service,
        filters=[
            lambda s: (s.name == service.name)
            & (s.estimated_time == service.estimated_time)
            & (s.price == service.price)
        ],
        tenant_id=request.state.tenant_id,
    )
    existing_service = services[0] if len(services) > 0 else None

    if existing_service:
        raise HTTPException(
            status_code=400,
            detail="A service with the same name, estimated time and price already exists.",
        )

    db_service = Service(
        name=service.name,
        estimated_time=service.estimated_time,
        price=service.price,
        image=service.image,
        description=service.description,
        tenant_id=request.state.tenant_id,
    )

    session.add(db_service)
    session.commit()
    session.refresh(db_service)

    return db_service


@router.delete("/services/delete/{service_id}", tags=["Services"])
async def delete_service(
    request: Request, service_id: int, session: SessionDep = SessionDep
):

    service = get_service_by_id(session, service_id, tenant_id=request.state.tenant_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    session.delete(service)
    session.commit()

    return {"message": f"Service {service_id} has been deleted."}


@router.put(
    "/services/update/{service_id}", tags=["Services"], response_model=ServicePublic
)
async def update_service(
    request: Request,
    service_id: int,
    service: service_validation.ServiceUpdateValidation,
    session: SessionDep = SessionDep,
):

    db_service = get_service_by_id(
        session, service_id, tenant_id=request.state.tenant_id
    )
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found.")

    service_data = service.model_dump(exclude_unset=True)
    db_service.sqlmodel_update(service_data)
    session.add(db_service)
    session.commit()
    session.refresh(db_service)

    return db_service


@router.get(
    "/services/tenant/{tenant_id}",
    tags=["Services"],
    response_model=list[ServicePublic],
)
async def get_service_by_tenant(
    tenant_id: int,
    session: SessionDep = SessionDep,
):

    services = select_by_tenant_id(session, Service, tenant_id=tenant_id)

    return services
