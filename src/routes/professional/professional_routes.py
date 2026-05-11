from fastapi import APIRouter, HTTPException, Request
from sqlmodel import select
from database.models.professional import Professional, ProfessionalPublic
from database.engine import SessionDep
from utils import get_professional_by_id, select_by_tenant_id
from validations import professional_validation

router = APIRouter()


@router.get(
    "/professionals/", tags=["Professionals"], response_model=list[ProfessionalPublic]
)
async def read_professionals(request: Request, session: SessionDep = SessionDep):
    professionals = select_by_tenant_id(
        session,
        Professional,
        tenant_id=request.state.tenant_id,
    )

    return professionals


@router.get(
    "/professionals/{professional_id}",
    tags=["Professionals"],
    response_model=ProfessionalPublic,
)
async def read_professional(
    request: Request, professional_id: int, session: SessionDep = SessionDep
):

    professional = get_professional_by_id(
        session, professional_id, tenant_id=request.state.tenant_id
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found.")

    return professional


@router.post(
    "/professionals/create/",
    tags=["Professionals"],
    status_code=201,
    response_model=ProfessionalPublic,
)
async def create_professional(
    request: Request,
    professional: professional_validation.ProfessionalCreateValidation,
    session: SessionDep = SessionDep,
):
    professionals = select_by_tenant_id(
        session,
        Professional,
        filters=[
            lambda p: (p.name == professional.name)
            & (p.phone == professional.phone)
            & (p.title == professional.title)
        ],
        tenant_id=request.state.tenant_id,
    )
    existing_professional = professionals[0] if len(professionals) > 0 else None

    if existing_professional:
        raise HTTPException(
            status_code=400,
            detail="A professional with the same name, phone, and title already exists.",
        )

    db_professional = Professional(
        name=professional.name,
        phone=professional.phone,
        title=professional.title,
        tenant_id=request.state.tenant_id,
    )

    session.add(db_professional)
    session.commit()
    session.refresh(db_professional)

    return db_professional


@router.delete(
    "/professionals/delete/{professional_id}",
    tags=["Professionals"],
    response_model=ProfessionalPublic,
)
async def delete_professional(
    request: Request, professional_id: int, session: SessionDep = SessionDep
):

    professional = get_professional_by_id(
        session, professional_id, tenant_id=request.state.tenant_id
    )
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found.")
    session.delete(professional)
    session.commit()

    return {"message": f"Professional {professional_id} has been deleted."}


@router.put(
    "/professionals/update/{professional_id}",
    tags=["Professionals"],
    response_model=ProfessionalPublic,
)
async def update_professional(
    request: Request,
    professional_id: int,
    professional: professional_validation.ProfessionalUpdateValidation,
    session: SessionDep = SessionDep,
):

    db_professional = get_professional_by_id(
        session, professional_id, tenant_id=request.state.tenant_id
    )
    if not db_professional:
        raise HTTPException(status_code=404, detail="Professional not found.")

    professional_data = professional.model_dump(exclude_unset=True)
    db_professional.sqlmodel_update(professional_data)
    session.add(db_professional)
    session.commit()
    session.refresh(db_professional)

    return db_professional
