from datetime import datetime
from sqlalchemy.dialects.mysql import DATETIME
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship
from .base import Base
from .client import ClientPublic
from .professional import ProfessionalPublic
from .service import ServicePublic


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
    start_time: datetime = Field(nullable=False,
                                 sa_type=DATETIME(timezone=True, fsp=6))
    end_time: datetime = Field(nullable=False,
                               sa_type=DATETIME(timezone=True, fsp=6))

    client: "Client" = Relationship(back_populates="appointments")
    professional: "Professional" = Relationship(back_populates='appointments')
    service: "Service" = Relationship(back_populates='appointments')


class AppointmentPublic(Base):
    id: int
    start_time: datetime
    end_time: datetime
    client: ClientPublic
    professional: ProfessionalPublic
    service: ServicePublic

    class Config:
        from_attributes = True