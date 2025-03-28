from pydantic import BaseModel, field_validator
import re

class ProfessionalCreateValidation(BaseModel):
    name: str
    phone: str
    title: str

    @field_validator('phone')
    def validate_phone(cls, phone):
        # Verifica se o telefone contém apenas números
        if not re.match(r'^\d+$', phone):
            raise ValueError('phone number must contain only numbers.')

        # Verifica o tamanho do telefone (10 ou 11 caracteres)
        if len(phone) not in [10, 11]:
            raise ValueError(f'phone number must be 10 or 11 characters long. {len(phone)} characters was given.')

        return phone

class ProfessionalUpdateValidation(BaseModel):
    name: str | None = None
    phone: str | None = None
    title: str | None = None

    @field_validator('phone')
    def validate_phone(cls, phone):
        # Verifica se o telefone contém apenas números
        if not re.match(r'^\d+$', phone):
            raise ValueError('phone number must contain only numbers.')

        # Verifica o tamanho do telefone (10 ou 11 caracteres)
        if len(phone) not in [10, 11]:
            raise ValueError(f'phone number must be 10 or 11 characters long. {len(phone)} characters was given.')

        return phone