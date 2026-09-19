"""
Funções auxiliares e dependências para a aplicação
"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import settings
from models import Base

# Logger
logger = logging.getLogger(__name__)

# Variável global para armazenar o session maker
_async_session_maker = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependência para injetar sessão do banco de dados
    """
    global _async_session_maker
    if _async_session_maker is None:
        raise RuntimeError("Database not initialized. Call set_async_session_maker first.")
    
    async with _async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def set_async_session_maker(session_maker):
    """
    Define o session maker global
    """
    global _async_session_maker
    _async_session_maker = session_maker


async def init_db():
    """
    Inicializa o banco de dados e cria as tabelas
    """
    # Criar engine
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=20,
        max_overflow=0,
    )
    
    # Criar session maker
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Definir o maker global
    set_async_session_maker(async_session_maker)
    
    # Criar tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Banco de dados inicializado")
    
    return engine, async_session_maker


def hash_password(password: str) -> str:
    """
    Hash de senha usando bcrypt
    """
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hash: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    """
    import bcrypt
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))


def create_jwt_token(data: dict, expires_delta=None):
    """
    Cria um token JWT
    """
    from datetime import timedelta
    from jose import jwt
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_jwt_token(token: str):
    """
    Verifica e decodifica um token JWT
    """
    from jose import jwt, JWTError
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


from datetime import datetime
