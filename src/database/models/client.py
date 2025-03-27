from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from .base import Base

if TYPE_CHECKING:
    from .appointment import Appointment


class Client(Base, table=True):
    __tablename__: str = "clients"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    address: str = Field(nullable=False)
    phone: str = Field(nullable=False)

    appointments: list['Appointment'] = Relationship(back_populates='client')
