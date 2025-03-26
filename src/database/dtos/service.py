class ServiceCreate:
    name: str
    estimated_time: int
    price: float


class ServiceUpdate:
    id: int
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None
