from pydantic import BaseModel


class Contact(BaseModel):
    name: str
    email: str


class SendMailValidation(BaseModel):
    category: str
    content: str
    subject: str
    to: Contact
    origin: Contact
