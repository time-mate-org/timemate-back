from pydantic import BaseModel

class AppointmentCreateValidation(BaseModel):
    client_id: int
    professional_id: int
    service_id: int


class AppointmentUpdateValidation(BaseModel):
    client_id: int | None = None
    professional_id: int | None = None
    service_id: int | None = None
