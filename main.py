from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.engine import lifespan
from .database.models.base import Base
# from .routes import auth_routes, user_routes, product_routes
# from .middlewares.logging_middleware import LoggingMiddleware
from .config import settings

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
# app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
# app.include_router(user_routes.router, prefix="/users", tags=["Users"])
# app.include_router(product_routes.router,
#                    prefix="/products", tags=["Products"])

# Cria tabelas no banco de dados
# Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
