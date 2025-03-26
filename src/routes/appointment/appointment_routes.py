from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException
from sqlmodel import select
from database.models.appointment import Appointment
from database.models.client import Client
from database.models.service import Service
from database.models.professional import Professional
from database.engine import SessionDep
from validations import appointment_validation


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
    appointment_payload: appointment_validation.AppointmentCreateValidation,
    session: SessionDep = SessionDep
):
    if appointment_payload.start_time:
        try:
            datetime.fromisoformat(appointment_payload.start_time)
        except:
            raise HTTPException(
                status_code=400, detail="'start_time' must be a ISO formated date.")

    client = session.exec(select(Client).where(
        Client.id == appointment_payload.client_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail='Client not found.')

    professional = session.exec(select(Professional).where(
        Professional.id == appointment_payload.professional_id)).first()
    if not professional:
        raise HTTPException(status_code=404, detail='Professional not found.')

    service = session.exec(select(Service).where(
        Service.id == appointment_payload.service_id)).first()
    if not service:
        raise HTTPException(status_code=404, detail='Service not found.')

    # # calculando início e final do agendamento
    appointment_start_time = datetime.fromisoformat(
        appointment_payload.start_time)
    appointment_end_time = get_appointment_end_time(
        appointment_start_time, service)

    check_concurrent_appointment_conflicts(
        session,
        client,
        professional,
        appointment_start_time,
        appointment_end_time
    )

    db_appointment = Appointment(
        client_id=appointment_payload.client_id,
        professional_id=appointment_payload.professional_id,
        service_id=appointment_payload.service_id,
        start_time=appointment_start_time,
        end_time=appointment_end_time
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
    appointment_payload: appointment_validation.AppointmentUpdateValidation,
    session: SessionDep = SessionDep
):

    if appointment_payload.start_time:
        try:
            datetime.fromisoformat(appointment_payload.start_time)
        except:
            raise HTTPException(
                status_code=400, detail="'start_time' must be a ISO formated date.")

    db_appointment = session.get(Appointment, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail='Appointment not found.')

    new_client: Client | None = None
    if appointment_payload.client_id:
        new_client = session.exec(select(Client).where(
            Client.id == appointment_payload.client_id)).first()
    if appointment_payload.client_id and not new_client:
        raise HTTPException(status_code=404, detail='Client not found.')

    new_professional: Professional | None = None
    if appointment_payload.professional_id:
        new_professional = session.exec(select(Professional).where(
            Professional.id == appointment_payload.professional_id)).first()
    if appointment_payload.professional_id and not new_professional:
        raise HTTPException(status_code=404, detail='Professional not found.')

    new_service: Service | None = None
    if appointment_payload.service_id:
        new_service = session.exec(select(Service).where(
            Service.id == appointment_payload.service_id)).first()
    if appointment_payload.service_id and not new_service:
        raise HTTPException(status_code=404, detail='Service not found.')

    # tanto quando o agendamento tem seu início alterado como quando ele tem seu serviço atualizado
    # (estimated_time pode mudar) ele precisar ter o final recalculado
    new_appointment_start_time: datetime | None = None
    new_appointment_end_time: datetime | None = None
    if appointment_payload.start_time or appointment_payload.service_id:
        new_appointment_start_time = datetime.fromisoformat(
            appointment_payload.start_time) if appointment_payload.start_time else db_appointment.start_time
        new_appointment_end_time = get_appointment_end_time(
            new_appointment_start_time, new_service or db_appointment.service)

        check_concurrent_appointment_conflicts(
            session,
            new_client or db_appointment.client,
            new_professional or db_appointment.professional,
            new_appointment_start_time,
            new_appointment_end_time,
            appointment_id
        )

    appointment_data = appointment_payload.model_dump(exclude_unset=True)
    if appointment_payload.start_time or appointment_payload.service_id:
        appointment_data['start_time'] = new_appointment_start_time
        appointment_data['end_time'] = new_appointment_end_time

    db_appointment.sqlmodel_update(appointment_data)
    session.add(db_appointment)
    session.commit()
    session.refresh(db_appointment)

    return db_appointment


def get_appointment_end_time(start_time: datetime, service: Service):
    appointment_end_time = start_time + \
        timedelta(minutes=service.estimated_time, microseconds=-1)

    return appointment_end_time


"""
Checa conflitos de tempo entre agendamentos
session: database session
client: cliente do agendamento ou novo cliente buscado no update
professional: profissional do agendamento ou novo profissional buscado no update
new_appointment_start_time: início do agendamento
new_appointment_end_time: final
appointment_id: id do appointment que to atualizando(create é null) para não buscá-lo nos conflitantes
"""


def check_concurrent_appointment_conflicts(
    session: SessionDep,
    client: Client,
    professional: Professional,
    new_appointment_start_time: datetime,
    new_appointment_end_time: datetime,
    appointment_id: int | None = None
):
    print(f"\n\nclient: {client}\n\n")
    print(f"\n\nprofessional: {professional}\n\n")
    print(
        f"\n\nnew_appointment_start_time: {new_appointment_start_time}\n\n")
    print(f"\n\nnew_appointment_end_time: {new_appointment_end_time}\n\n")

    same_hour_appointments = session.exec(
        select(Appointment).where(
            ((  # ver se quando o novo começa tem algum ocorrendo
                (new_appointment_start_time >= Appointment.start_time) &
                (new_appointment_start_time < Appointment.end_time)
            ) |
                (  # ver se quando o novo termina tem algum ocorrendo
                (new_appointment_end_time > Appointment.start_time) &
                (new_appointment_end_time <= Appointment.end_time)
            )) & (
                # não pegar o mesmo que estou atualizando,
                Appointment.id != appointment_id
            )
        )
    ).all()

    print(f"\n\nSame hour appointments: {same_hour_appointments}\n\n")
    same_client_and_same_hour_appointments = list(filter(
        lambda appt: appt.client_id == client.id,
        same_hour_appointments)
    )

    print(
        f"\n\nSame hour same_client_and_same_hour_appointments: {same_client_and_same_hour_appointments}\n\n")
    if len(same_client_and_same_hour_appointments) > 0:
        raise HTTPException(
            status_code=409,
            detail="There's an appointment with the same client for the same time slot."
        )

    # um profissional não pode estar em dois agendamentos na mesma hora
    same_professional_and_same_hour_appointments = list(filter(
        lambda appt: appt.professional_id == professional.id,
        same_hour_appointments
    ))

    if len(same_professional_and_same_hour_appointments) > 0:
        raise HTTPException(
            status_code=409,
            detail="There's an appointment with the same professional for the same time slot."
        )
