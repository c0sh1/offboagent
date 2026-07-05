"""
Punto de entrada de la aplicación FastAPI.

Ejecutar con: uvicorn app.main:app --reload
Después abre: http://127.0.0.1:8000/docs (documentación interactiva automática)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import Base, engine
from app.api.persons import router as persons_router
from app.api.offboarding import router as offboarding_router
from app.api.security import router as security_router
from app.api.dashboard import router as dashboard_router
from app.api.systems import router as systems_router

app = FastAPI(
    title="Offboarding Security Agent",
    description="Agente de IA para offboarding seguro de empleados/contratistas",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(persons_router)
app.include_router(offboarding_router)
app.include_router(security_router)
app.include_router(dashboard_router)
app.include_router(systems_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "offboarding-agent"}