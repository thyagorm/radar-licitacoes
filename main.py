from services.scheduler_service import iniciar_agendador, parar_agendador
from routers import alerts_router
"""
Radar de Licitações - Aplicação FastAPI
Sistema inteligente de monitoramento de contratações públicas
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from config import settings
from utils import init_db
from routers import pncp_router, edital_analyzer, admin_logs,  users, licitations, matches, notifications, dashboard, cmed_prices

# Configurar logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    # Startup
    logger.info("🚀 Iniciando Radar de Licitações...")
    try:
        engine, async_session_maker = await init_db()
        logger.info("✅ Banco de dados inicializado")
        logger.info("✅ Aplicação pronta!")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando aplicação...")
    await engine.dispose()
    logger.info("✅ Aplicação encerrada")


# Criar aplicação FastAPI
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Incluir routers


@app.on_event("startup")
async def ao_iniciar_aplicacao():
    iniciar_agendador()

@app.on_event("shutdown")
async def ao_encerrar_aplicacao():
    parar_agendador()

app.include_router(alerts_router.router, prefix="/api/alerts", tags=["Alertas & Notificações"])
app.include_router(pncp_router.router, prefix="/api/pncp", tags=["Editais PNCP"])
app.include_router(edital_analyzer.router, prefix="/api/analyzer", tags=["analyzer"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(licitations.router, prefix="/api/licitations", tags=["licitations"])
app.include_router(matches.router, prefix="/api/matches", tags=["matches"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(cmed_prices.router, prefix="/api/cmed-prices", tags=["cmed-prices"])


# Health Check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.api_version,
        "test_mode": settings.test_mode
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - redireciona para o dashboard"""
    return {
        "message": "🎯 Radar de Licitações",
        "version": settings.api_version,
        "docs": "/docs",
        "dashboard": "/static/index.html"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False
    )
