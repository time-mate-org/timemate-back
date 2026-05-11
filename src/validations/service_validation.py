from pydantic import BaseModel


class ServiceCreateValidation(BaseModel):
    name: str
    estimated_time: int
    price: float
    image: str
    description: str


class ServiceUpdateValidation(BaseModel):
    name: str | None = None
    estimated_time: int | None = None
    price: float | None = None
    image: str | None = None
    description: str | None = None
