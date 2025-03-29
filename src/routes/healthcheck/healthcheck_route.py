from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse


router = APIRouter()

@router.get("/health/", tags=["Health"])
async def health_check():

    return JSONResponse(content={"Status": "OK"}, status_code=200)