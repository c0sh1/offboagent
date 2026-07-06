"""
Punto de entrada de la aplicación FastAPI.

Ejecutar con: uvicorn app.main:app --reload
Después abre: http://127.0.0.1:8000/docs (documentación interactiva automática)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import Base, engine
from app.config import settings
from app.api.persons import router as persons_router
from app.api.offboarding import router as offboarding_router
from app.api.security import router as security_router
from app.api.dashboard import router as dashboard_router
from app.api.systems import router as systems_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI(
    title="Offboarding Security Agent",
    description="Agente de IA para offboarding seguro de empleados/contratistas",
    version="0.1.0",
)

# CORS: permite que el frontend (React en localhost:5173 durante desarrollo)
# pueda llamar a esta API desde el navegador. Sin esto, el navegador
# bloquea las peticiones por política de same-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas si no existen (equivalente a lo que hace scripts/init_db.py)
Base.metadata.create_all(bind=engine)

# Aviso de seguridad: si nunca configuraste tu propia JWT_SECRET_KEY,
# todos los tokens se firman con el valor de ejemplo que está escrito
# en el código fuente (visible para cualquiera que vea el repo).
# Cualquiera que lo conozca podría falsificar tokens de sesión válidos.
_DEFAULT_JWT_SECRET = "cambia-esto-en-produccion-por-algo-aleatorio-y-largo"
if settings.jwt_secret_key == _DEFAULT_JWT_SECRET:
    print(
        "\n⚠️  ADVERTENCIA DE SEGURIDAD: estás usando el JWT_SECRET_KEY de ejemplo.\n"
        "   Cualquiera que vea este código podría falsificar sesiones válidas.\n"
        "   Configura una clave propia, larga y aleatoria, en tu archivo .env\n"
        "   antes de usar esto con datos reales.\n"
    )

app.include_router(persons_router)
app.include_router(offboarding_router)
app.include_router(security_router)
app.include_router(dashboard_router)
app.include_router(systems_router)
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "offboarding-agent"}