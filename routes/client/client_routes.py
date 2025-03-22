from fastapi import APIRouter, HTTPException
from sqlmodel import select
from ...database.models.client import Client
from ...database.engine import SessionDep
from ...validations import client_validation


router = APIRouter()

@router.get("/clients/", tags=["Clients"])
async def read_clients(session: SessionDep = SessionDep):

    statement = select(Client)
    clients = session.exec(statement).all()

    return clients


@router.get("/clients/{client_id}", tags=["Clients"])
async def read_client(client_id: int, session: SessionDep = SessionDep):

    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found.')
    
    return client


@router.post("/clients/create/", tags=["Clients"], status_code=201)
async def create_client(client: client_validation.ClientCreateValidation, session: SessionDep = SessionDep):

    db_client = Client(
        name=client.name,
        address=client.address,
        phone=client.phone,
    )

    session.add(db_client)
    session.commit()
    session.refresh(db_client)

    return db_client


@router.delete("/clients/delete/{client_id}", tags=["Clients"])
async def delet_client(client_id: int, session: SessionDep = SessionDep):

    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found.')
    session.delete(client)
    session.commit()

    return {"message": f"Client {client_id} has been deleted."}


@router.put("/clients/update/{client_id}", tags=["Clients"])
async def update_client(client_id: int, client: client_validation.ClientUpdateValidation,
                    session: SessionDep = SessionDep):

    db_client = session.get(Client, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail='Client not found.')
    
    client_data = client.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(client_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)

    return db_client
