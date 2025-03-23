from pydantic import BaseModel

class ProfessionalCreateValidation(BaseModel):
    name: str
    phone: str
    title: str


class ProfessionalUpdateValidation(BaseModel):
    name: str | None = None
    phone: str | None = None
    title: str | None = None
