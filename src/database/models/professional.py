from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship
from .base import Base

if TYPE_CHECKING:
    from .appointment import Appointment

DEFAULT_TITLE = "barbeiro"


class Professional(Base, table=True):
    __tablename__: str = "professionals"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    phone: str = Field(nullable=False)
    title: str = Field(default=DEFAULT_TITLE, nullable=False)

    appointments: List["Appointment"] = Relationship(back_populates="professional")

    tenant_id: int | None = Field(
        default=None, foreign_key="tenants.id", ondelete="SET NULL"
    )


class ProfessionalPublic(Base):
    id: int
    name: str
    phone: str
    title: str
    tenant_id: int | None

    class Config:
        from_attributes = True
