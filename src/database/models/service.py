from sqlmodel import Field, Relationship
from typing import TYPE_CHECKING, List
from .base import Base

if TYPE_CHECKING:
    from .appointment import Appointment


class Service(Base, table=True):
    __tablename__: str = "services"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    estimated_time: int = Field(nullable=False)
    price: float = Field(nullable=False)

    appointments: List["Appointment"] = Relationship(back_populates='service')

class ServicePublic(Base):
    id: int
    name: str
    estimated_time: int
    price: float

    class Config:
        from_attributes = True