from typing import List, Optional
from sqlmodel import ARRAY, JSON, Column, Field, String, Text
from .base import Base


class Tenant(Base, table=True):
    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)  # ex: "tenant_abc"
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    phone: str = Field(nullable=False)
    whatsapp: str | None = Field(default=None)
    address: str = Field(nullable=False)
    availability: str = Field(nullable=False)  # ex: "Mon-Fri 9am-5pm"
    is_active: bool = Field(default=True)
    logo: str | None = Field(default=None)  # tenant bucket logo path

    blog_photos: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    blog_title: str = Field(nullable=False)
    blog_subtitle: str = Field(nullable=False)
    blog_about: str | None = Field(default=None, sa_type=Text())
