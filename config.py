from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Team Mate"
    admin_email: str = 'teammate@ennes.dev'
    db_connectin: str = ''


settings = Settings()
