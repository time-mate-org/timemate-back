from fastapi import APIRouter, HTTPException
from sqlmodel import select
from ...database.models.service import Service
from ...database.engine import SessionDep
from ...validations import service_validation


router = APIRouter()

@router.get("/services/", tags=["Services"])
async def read_services(session: SessionDep = SessionDep):

    statement = select(Service)
    services = session.exec(statement).all()

    return services


@router.get("/services/{service_id}", tags=["Services"])
async def read_service(service_id: int, session: SessionDep = SessionDep):

    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail='Service not found.')
    
    return service


@router.post("/services/create/", tags=["Services"], status_code=201)
async def create_service(
    service: service_validation.ServiceCreateValidation,
    session: SessionDep = SessionDep
    ):

    existing_service = session.exec(
        select(Service).where(
            (Service.name == service.name) &
            (Service.estimated_time == service.estimated_time) &
            (Service.price == service.price)
        )
    ).first()

    if existing_service:
        raise HTTPException(
            status_code=400,
            detail="A service with the same name, estimated time and price already exists."
        )
        
    db_service = Service(
        name=service.name,
        estimated_time=service.estimated_time,
        price=service.price,
    )

    session.add(db_service)
    session.commit()
    session.refresh(db_service)

    return db_service


@router.delete("/services/delete/{service_id}", tags=["Services"])
async def delete_service(service_id: int, session: SessionDep = SessionDep):

    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail='Service not found.')
    session.delete(service)
    session.commit()

    return {"message": f"Service {service_id} has been deleted."}


@router.put("/services/update/{service_id}", tags=["Services"])
async def update_service(
                service_id: int,
                service: service_validation.ServiceUpdateValidation,
                session: SessionDep = SessionDep
                ):

    db_service = session.get(Service, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail='Service not found.')
    
    service_data = service.model_dump(exclude_unset=True)
    db_service.sqlmodel_update(service_data)
    session.add(db_service)
    session.commit()
    session.refresh(db_service)

    return db_service
