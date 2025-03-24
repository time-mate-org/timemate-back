from fastapi import APIRouter, HTTPException
from sqlmodel import select
from ...database.models.appointment import Appointment
from ...database.models.client import Client
from ...database.models.service import Service
from ...database.models.professional import Professional
from ...database.engine import SessionDep
from ...validations import appointment_validation


router = APIRouter()

@router.get("/appointments/", tags=["Appointments"])
async def read_appointments(session: SessionDep = SessionDep):

    statement = select(Appointment)
    appointments = session.exec(statement).all()

    return appointments


@router.get("/appointments/{appointment_id}", tags=["Appointments"])
async def read_appointment(appointment_id: int, session: SessionDep = SessionDep):

    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail='Appointment not found.')
    
    return appointment


@router.post("/appointments/create/", tags=["Appointments"], status_code=201)
async def create_appointment(
    appointment: appointment_validation.AppointmentCreateValidation,
    session: SessionDep = SessionDep
    ):

    existing_appointment = session.exec(
        select(Appointment).where(
            (Appointment.client_id == appointment.client_id) &
            (Appointment.professional_id == appointment.professional_id) &
            (Appointment.service_id == appointment.service_id)
        )
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="A appointment with the same client, professional, and service already exists."
        )
    
    client_exists = session.exec(select(Client).where(Client.id == appointment.client_id)).first()
    if not client_exists:
        raise HTTPException(status_code=404, detail='Client not found.')
    
    professional_exists = session.exec(select(Professional).where(Professional.id == appointment.professional_id)).first()
    if not professional_exists:
        raise HTTPException(status_code=404, detail='Professional not found.')
    
    service_exists = session.exec(select(Service).where(Service.id == appointment.service_id)).first()
    if not service_exists:
        raise HTTPException(status_code=404, detail='Service not found.')
        
    db_appointment = Appointment(
        client_id=appointment.client_id,
        professional_id=appointment.professional_id,
        service_id=appointment.service_id,
    )

    session.add(db_appointment)
    session.commit()
    session.refresh(db_appointment)

    return db_appointment


@router.delete("/appointments/delete/{appointment_id}", tags=["Appointments"])
async def delete_appointment(appointment_id: int, session: SessionDep = SessionDep):

    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail='Appointment not found.')
    session.delete(appointment)
    session.commit()

    return {"message": f"Appointment {appointment_id} has been deleted."}


@router.put("/appointments/update/{appointment_id}", tags=["Appointments"])
async def update_appointment(
                appointment_id: int,
                appointment: appointment_validation.AppointmentUpdateValidation,
                session: SessionDep = SessionDep
                ):

    db_appointment = session.get(Appointment, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail='Appointment not found.')
    
    client_exists = session.exec(select(Client).where(Client.id == appointment.client_id)).first()
    if not client_exists:
        raise HTTPException(status_code=404, detail='Client not found.')
    
    professional_exists = session.exec(select(Professional).where(Professional.id == appointment.professional_id)).first()
    if not professional_exists:
        raise HTTPException(status_code=404, detail='Professional not found.')
    
    service_exists = session.exec(select(Service).where(Service.id == appointment.service_id)).first()
    if not service_exists:
        raise HTTPException(status_code=404, detail='Service not found.')
    
    appointment_data = appointment.model_dump(exclude_unset=True)
    db_appointment.sqlmodel_update(appointment_data)
    session.add(db_appointment)
    session.commit()
    session.refresh(db_appointment)

    return db_appointment
