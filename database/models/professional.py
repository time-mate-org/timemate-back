from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from .base import Base

if TYPE_CHECKING:
    from .appointment import Appointment

DEFAULT_TITLE = 'barbeiro'


class Professional(Base, table=True):
    __tablename__: str = "professionals"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    phone: str = Field(nullable=False)
    title: str = Field(default=DEFAULT_TITLE, nullable=False)

    appointments: list['Appointment'] = Relationship(
        back_populates='professional')
