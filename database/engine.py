import os
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine
from .models.base import Base
from .models import *

mysql_url = os.getenv("MYSQL_URI").replace("mysql://", "mysql+pymysql://")
mysql_url += "?ssl_ca=./database/ca.pem"
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
    print("Criando tablelas.")
    create_db_and_tables()
    yield


# @app.post("/heroes/", response_model=HeroPublic)
# def create_hero(hero: HeroCreate, session: SessionDep):
#     db_hero = Hero.model_validate(hero)
#     session.add(db_hero)
#     session.commit()
#     session.refresh(db_hero)
#     return db_hero


# @app.get("/heroes/", response_model=list[HeroPublic])
# def read_heroes(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ):
#     heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
#     return heroes


# @app.get("/heroes/{hero_id}", response_model=HeroPublic)
# def read_hero(hero_id: int, session: SessionDep):
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     return hero


# @app.patch("/heroes/{hero_id}", response_model=HeroPublic)
# def update_hero(hero_id: int, hero: HeroUpdate, session: SessionDep):
#     hero_db = session.get(Hero, hero_id)
#     if not hero_db:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     hero_data = hero.model_dump(exclude_unset=True)
#     hero_db.sqlmodel_update(hero_data)
#     session.add(hero_db)
#     session.commit()
#     session.refresh(hero_db)
#     return hero_db


# @app.delete("/heroes/{hero_id}")
# def delete_hero(hero_id: int, session: SessionDep):
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     session.delete(hero)
#     session.commit()
#     return {"ok": True}
