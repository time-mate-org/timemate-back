import os
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine
from .models.base import Base
from .models import *

mysql_url = os.getenv("MYSQL_URI")
# mysql_url += "?ssl_ca=./database/ca.pem"
engine = create_engine(mysql_url, echo=True)

def create_db_and_tables():
    try:            
        Base.metadata.create_all(engine)
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # coisas que precisam ser executadas antes da aplicação
    yield
    # coisas que precisam ser executas após a aplicação finalizar
