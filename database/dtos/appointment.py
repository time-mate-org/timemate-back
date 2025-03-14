class AppointmentCreate:
    client_id: int
    service_id: int
    professional_id: int


class AppointmentUpdate:
    id: int
    client_id: int | None
    service_id: int | None
    professional_id: int | None
