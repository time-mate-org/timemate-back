class ServiceCreate:
    name: str
    estimated_time: int
    price: float
    image: str
    description: str


class ServiceUpdate:
    id: int
    name: str | None = None
    age: int | None = None
    secret_name: str | None = None
    image: str | None = None
    description: str | None = None
