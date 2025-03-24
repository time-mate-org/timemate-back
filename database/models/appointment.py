from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from .base import Base

if TYPE_CHECKING:
    from .client import Client
    from .professional import Professional
    from .service import Service


class Appointment(Base, table=True):
    __tablename__: str = "appointments"
    id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.id")
    service_id: int = Field(foreign_key="services.id")
    professional_id: int = Field(foreign_key="professionals.id")

    client: "Client" = Relationship(back_populates="appointments")
    professional: "Professional" = Relationship(back_populates='appointments')
    service: "Service" = Relationship(back_populates='appointments')
