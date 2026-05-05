from typing import TYPE_CHECKING, List
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

    appointments: List['Appointment'] = Relationship(back_populates='client')
    
    tenant_id: int | None = Field(default=None, foreign_key="tenants.id", ondelete="SET NULL")


class ClientPublic(Base):
    id: int
    name: str
    address: str
    phone: str
    tenant_id: int | None

    class Config:
        from_attributes = True