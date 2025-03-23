from fastapi import APIRouter, HTTPException
from sqlmodel import select
from ...database.models.professional import Professional
from ...database.engine import SessionDep
from ...validations import professional_validation


router = APIRouter()

@router.get("/professionals/", tags=["Professionals"])
async def read_professionals(session: SessionDep = SessionDep):

    statement = select(Professional)
    professionals = session.exec(statement).all()

    return professionals


@router.get("/professionals/{professional_id}", tags=["Professionals"])
async def read_professional(professional_id: int, session: SessionDep = SessionDep):

    professional = session.get(Professional, professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail='Professional not found.')
    
    return professional


@router.post("/professionals/create/", tags=["Professionals"], status_code=201)
async def create_professional(
    professional: professional_validation.ProfessionalCreateValidation,
    session: SessionDep = SessionDep
    ):

    existing_professional = session.exec(
        select(Professional).where(
            (Professional.name == professional.name) &
            (Professional.phone == professional.phone) &
            (Professional.title == professional.title)
        )
    ).first()

    if existing_professional:
        raise HTTPException(
            status_code=400,
            detail="A professional with the same name, phone, and title already exists."
        )
        
    db_professional = Professional(
        name=professional.name,
        phone=professional.phone,
        title=professional.title,
    )

    session.add(db_professional)
    session.commit()
    session.refresh(db_professional)

    return db_professional


@router.delete("/professionals/delete/{professional_id}", tags=["Professionals"])
async def delete_professional(professional_id: int, session: SessionDep = SessionDep):

    professional = session.get(Professional, professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail='Professional not found.')
    session.delete(professional)
    session.commit()

    return {"message": f"Professional {professional_id} has been deleted."}


@router.put("/professionals/update/{professional_id}", tags=["Professionals"])
async def update_professional(
                professional_id: int,
                professional: professional_validation.ProfessionalUpdateValidation,
                session: SessionDep = SessionDep
                ):

    db_professional = session.get(Professional, professional_id)
    if not db_professional:
        raise HTTPException(status_code=404, detail='Professional not found.')
    
    professional_data = professional.model_dump(exclude_unset=True)
    db_professional.sqlmodel_update(professional_data)
    session.add(db_professional)
    session.commit()
    session.refresh(db_professional)

    return db_professional
