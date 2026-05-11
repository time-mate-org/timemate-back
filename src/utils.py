from typing import Callable, Type
from sqlalchemy import BinaryExpression
from sqlmodel import SQLModel, Session, select
from sqlalchemy.orm import QueryableAttribute, selectinload
from database.models import Client, Professional, Appointment, Service


def select_by_tenant_id(
    session: Session,
    model: Type[SQLModel],
    tenant_id: int,
    filters: Callable[[type[SQLModel]], BinaryExpression] = [],
    load: list[QueryableAttribute] = [],
) -> list[SQLModel]:
    statement = (
        select(model)
        .where(model.tenant_id == tenant_id)
        .options(
            *load,
        )
    )

    for f in filters:
        statement = statement.where(f(model) if callable(f) else f)

    return session.exec(statement).all()


def get_appointment_by_id(
    session: Session, appointment_id: int, tenant_id: int
) -> Appointment | None:
    appointments = select_by_tenant_id(
        session,
        Appointment,
        tenant_id=tenant_id,
        filters=[lambda a: a.id == appointment_id],
        load=[
            selectinload(Appointment.client),
            selectinload(Appointment.professional),
            selectinload(Appointment.service),
        ],
    )

    return appointments[0] if len(appointments) > 0 else None


def get_client_by_id(session: Session, client_id: int, tenant_id: int) -> Client | None:
    clients = select_by_tenant_id(
        session,
        Client,
        tenant_id=tenant_id,
        filters=[lambda c: c.id == client_id],
        load=[selectinload(Client.appointments)],
    )

    return clients[0] if len(clients) > 0 else None


def get_professional_by_id(
    session: Session, professional_id: int, tenant_id: int
) -> Professional | None:
    professionals = select_by_tenant_id(
        session,
        Professional,
        tenant_id=tenant_id,
        filters=[lambda p: p.id == professional_id],
        load=[selectinload(Professional.appointments)],
    )

    return professionals[0] if len(professionals) > 0 else None


def get_service_by_id(
    session: Session, service_id: int, tenant_id: int
) -> Service | None:

    services = select_by_tenant_id(
        session,
        Service,
        tenant_id=tenant_id,
        filters=[lambda s: s.id == service_id],
        load=[selectinload(Service.appointments)],
    )

    return services[0] if len(services) > 0 else None
