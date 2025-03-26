class ProfessionalCreate:
    name: str
    phone: str
    title: str


class ProfessionalUpdate:
    id: int
    name: str | None
    phone: str | None
    title: str | None
