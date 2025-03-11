from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Team Mate"
    admin_email: str = 'teammate@ennes.dev'
    db_connectin: str = ''
    hashing_secret: str = '8064be1db0b010b31844b0da5c8f29dc63db18453e5377f59dadb0c2d9463e88'


settings = Settings()
