from pydantic import BaseModel

class ClientCreateValidation(BaseModel):
    name: str
    address: str
    phone: str


class ClientUpdateValidation(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
