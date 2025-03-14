from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .appointment import Appointment


class Service(Base, table=True):
    __tablename__: str = "services"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    estimated_time: int = Field(nullable=False)
    price: float = Field(nullable=False)

    appointments: list["Appointment"] = Relationship(
        back_populates='service')
