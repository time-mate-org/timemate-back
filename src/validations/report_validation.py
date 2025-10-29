from pydantic import BaseModel
from datetime import date


class ReportRequest(BaseModel):
    professional_id: int
    start_date: date
    end_date: date
