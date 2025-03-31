from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from database.engine import lifespan
from routes.client import client_routes
from routes.professional import professional_routes
from routes.service import service_routes
from routes.appointment import appointment_routes
from routes.healthcheck import healthcheck_route
from config import settings
from middleware.auth import authMiddleware

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://timemate-front.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
app.add_middleware(BaseHTTPMiddleware, dispatch=authMiddleware)

security_scheme = HTTPBearer(auto_error=False)
# Rotas
app.include_router(client_routes.router, tags=[
                   "Clients"], dependencies=[Depends(security_scheme)])
app.include_router(professional_routes.router, tags=[
                   "Professionals"], dependencies=[Depends(security_scheme)])
app.include_router(service_routes.router, tags=[
                   "Services"], dependencies=[Depends(security_scheme)])
app.include_router(appointment_routes.router, tags=[
                   "Appointments"], dependencies=[Depends(security_scheme)])

app.include_router(healthcheck_route.router, tags=["Health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
