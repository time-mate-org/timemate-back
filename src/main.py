from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.engine import lifespan
from routes.client import client_routes
from routes.professional import professional_routes
from routes.service import service_routes
from routes.appointment import appointment_routes
from routes.healthcheck import healthcheck_route
# from .routes import auth_routes, user_routes, product_routes
# from .middlewares.logging_middleware import LoggingMiddleware
from config import settings

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(LoggingMiddleware)  # Middleware personalizado

# Rotas
app.include_router(healthcheck_route.router, tags=["Health"])
app.include_router(client_routes.router, tags=["Clients"])
app.include_router(professional_routes.router, tags=["Professionals"])
app.include_router(service_routes.router, tags=["Services"])
app.include_router(appointment_routes.router, tags=["Appointments"])
# app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
# app.include_router(user_routes.router, prefix="/users", tags=["Users"])
# app.include_router(product_routes.router, prefix="/products", tags=["Products"])

# Cria tabelas no banco de dados
# Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
