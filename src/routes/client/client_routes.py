from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from database.models.client import Client, ClientPublic
from database.engine import SessionDep
from utils import get_client_by_id, select_by_tenant_id
from validations import client_validation
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/clients/", tags=["Clients"], response_model=list[ClientPublic])
async def read_clients(request: Request, session: SessionDep = SessionDep):
    clients = select_by_tenant_id(
        session,
        Client,
        tenant_id=request.state.tenant_id,
        load=[selectinload(Client.appointments)],
    )

    return clients


@router.get("/clients/{client_id}", tags=["Clients"], response_model=ClientPublic)
async def read_client(
    request: Request, client_id: int, session: SessionDep = SessionDep
):
    client = get_client_by_id(session, client_id, request.state.tenant_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")

    return client


@router.post(
    "/clients/create/", tags=["Clients"], status_code=201, response_model=ClientPublic
)
async def create_client(
    request: Request,
    client: client_validation.ClientCreateValidation,
    session: SessionDep = SessionDep,
):
    clients = select_by_tenant_id(
        session,
        Client,
        filters=[
            lambda c: (c.name == client.name)
            & (c.phone == client.phone)
            & (c.address == client.address)
        ],
        tenant_id=request.state.tenant_id,
    )

    existing_client = clients[0] if len(clients) > 0 else None
    if existing_client:
        raise HTTPException(
            status_code=400,
            detail="A client with the same name, phone and address already exists.",
        )

    db_client = Client(
        name=client.name,
        address=client.address,
        phone=client.phone,
        tenant_id=request.state.tenant_id,
    )

    session.add(db_client)
    session.commit()
    session.refresh(db_client)

    return db_client


@router.delete("/clients/delete/{client_id}", tags=["Clients"])
async def delete_client(
    request: Request, client_id: int, session: SessionDep = SessionDep
):
    client = get_client_by_id(session, client_id, tenant_id=request.state.tenant_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found.")

    session.delete(client)
    session.commit()

    return {"message": f"Client {client_id} has been deleted."}


@router.put(
    "/clients/update/{client_id}", tags=["Clients"], response_model=ClientPublic
)
async def update_client(
    request: Request,
    client_id: int,
    client: client_validation.ClientUpdateValidation,
    session: SessionDep = SessionDep,
):
    db_client = get_client_by_id(session, client_id, tenant_id=request.state.tenant_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found.")

    client_data = client.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(client_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)

    return db_client
