from pydantic import BaseModel

class AppointmentCreateValidation(BaseModel):
    client_id: int
    professional_id: int
    service_id: int
    start_time: str


class AppointmentUpdateValidation(BaseModel):
    client_id: int | None = None
    professional_id: int | None = None
    service_id: int | None = None
    start_time: str | None = None
