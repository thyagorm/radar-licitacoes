import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from datetime import datetime

from .config import settings
from .models import Base
from .utils import set_async_session_maker

# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variável global para session do banco
async_engine = None
async_session_maker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager para startup/shutdown da aplicação"""
    
    # ===== STARTUP =====
    logger.info("🚀 Iniciando Radar de Licitações...")
    
    global async_engine, async_session_maker
    
    try:
        # Inicializar banco de dados
        async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_size=20,
            max_overflow=30
        )
        
        async_session_maker = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Definir o maker global
        set_async_session_maker(async_session_maker)
        
        # Criar tabelas
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Banco de dados inicializado")
        logger.info("✅ Aplicação pronta!")
    
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar: {e}", exc_info=True)
        raise
    
    yield
    
    # ===== SHUTDOWN =====
    logger.info("🛑 Encerrando aplicação...")
    
    try:
        if async_engine:
            await async_engine.dispose()
        logger.info("✅ Aplicação encerrada")
    except Exception as e:
        logger.error(f"Erro ao encerrar: {e}")

# Criar aplicação FastAPI
app = FastAPI(
    title="Radar de Licitações",
    description="Sistema inteligente de monitoramento de contratações públicas",
    version="1.0.0",
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
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Importar routers APÓS criar a app
from .routers import users, portfolio, licitations, matches, notifications, dashboard

# ===== ROUTERS =====
app.include_router(
    users.router,
    prefix="/api/users",
    tags=["Users"]
)

app.include_router(
    portfolio.router,
    prefix="/api/portfolio",
    tags=["Portfolio"]
)

app.include_router(
    licitations.router,
    prefix="/api/licitations",
    tags=["Licitations"]
)

app.include_router(
    matches.router,
    prefix="/api/matches",
    tags=["Matches"]
)

app.include_router(
    notifications.router,
    prefix="/api/notifications",
    tags=["Notifications"]
)

app.include_router(
    dashboard.router,
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

# ===== HEALTH CHECK =====
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ===== ROOT =====
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - redireciona para frontend"""
    from fastapi.responses import FileResponse
    static_dir = Path(__file__).parent / "static"
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "name": "Radar de Licitações",
        "description": "Sistema inteligente de monitoramento de contratações públicas",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "users": "/api/users",
            "portfolio": "/api/portfolio",
            "licitations": "/api/licitations",
            "matches": "/api/matches",
            "notifications": "/api/notifications",
            "dashboard": "/api/dashboard"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "radar_licitacoes.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.LOG_LEVEL == "DEBUG"
    )
