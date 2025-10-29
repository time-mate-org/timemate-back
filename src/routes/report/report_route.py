from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import select
from database.models.client import Client
from database.models.professional import Professional
from database.models.appointment import Appointment
from database.models.service import Service
from database.engine import SessionDep
from io import BytesIO
from validations import report_validation
from routes.utils.pdf_generator import generate_report_pdf

from datetime import datetime, time


router = APIRouter()


@router.post("/report/", tags=["Report"], response_class=StreamingResponse)
async def generate_report(request: report_validation.ReportRequest, session: SessionDep = SessionDep):
    prof_statement = (
        select(Professional.name)
        .where(Professional.id == request.professional_id))
    
    professional_name = session.exec(prof_statement).first()
    
    if not professional_name:
        raise HTTPException(status_code=404, detail="Professional not found")

    start_date = datetime.combine(request.start_date, time.min)
    end_date = datetime.combine(request.end_date, time.max)

    statement = (
        select(Appointment, Client, Service)
        .join(Client, Appointment.client_id == Client.id)
        .join(Service, Appointment.service_id == Service.id)
        .where(
            Appointment.professional_id == request.professional_id,
            Appointment.start_time >= start_date,
            Appointment.start_time <= end_date
        )
    )
    results = session.exec(statement).all()
    report = [
        [
            appointment.start_time.strftime('%d/%m/%Y'),
            client.name,
            service.name,
            service.price
        ]
        for appointment, client, service in results
    ]

    report_data = {
                'name': professional_name, 
                'period': f'{request.start_date.strftime('%d/%m/%Y')} a {request.end_date.strftime('%d/%m/%Y')}',
                'appointments': report
    }

    cleaned_professional_name = professional_name.title().replace(' ', '')

    pdf_bytes = generate_report_pdf(report_data)
    
    if request.start_date == request.end_date:
        filename = f"Relatorio_{cleaned_professional_name}_{start_date.strftime('%d-%m-%Y')}.pdf"
    else:
        filename = f"Relatorio_{cleaned_professional_name}_{start_date.strftime('%d-%m-%Y')}_a_{end_date.strftime('%d-%m-%Y')}.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )