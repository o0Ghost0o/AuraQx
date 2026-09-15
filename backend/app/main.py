import sys
from pathlib import Path

# Garantizar que el directorio backend esté en sys.path para comandos de fastapi-cli
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from app.routers.auth_router import router as auth_router
from app.routers.demo_router import router as demo_router
from app.routers.notion_router import router as notion_router
from app.routers.preauth import router as preauth_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agente de Pre-Autorización Quirúrgica en Tiempo Real (Reto 1 HackIAthon Viamatica/ADEN)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En hackathon permitimos conexiones desde PWA Nuxt y túneles
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de Routers
app.include_router(auth_router)
app.include_router(preauth_router)
app.include_router(notion_router)
app.include_router(demo_router)


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "security": {
            "access_token_expire_minutes": settings.access_token_expire_minutes,
            "refresh_token_expire_days": settings.refresh_token_expire_days,
        },
        "llm_provider": {
            "base_url": settings.openai_base_url,
            "model": settings.openai_model,
        },
    }
