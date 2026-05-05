from sqlmodel import Field
from .base import Base

class User(Base, table=True):
  __tablename__: str = "users"
  
  id: int | None = Field(default=None, primary_key=True)
  uid: str = Field(nullable=False, unique=True)  # Firebase UID
  email: str = Field(nullable=False, unique=True)
  tenant_id: int | None = Field(default=None, foreign_key="tenants.id", ondelete="SET NULL")
  role: str = Field(nullable=False)  # 'admin', 'professional', 'client', etc.