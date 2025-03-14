class ClientCreate:
    name: str
    address: str
    phone: str


class ClientUpdate:
    id: int
    name: str | None
    address: str | None
    phone: str | None
