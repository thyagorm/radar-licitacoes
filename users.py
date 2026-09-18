from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
import logging

from ..config import settings
from ..models import User
from ..utils import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    phone: str
    cnpj: str
    company_name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    company_name: str
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_db)):
    """Registrar novo usuário"""
    
    # Verificar se email já existe
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Hash da senha
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"])
    
    new_user = User(
        email=user_data.email,
        phone=user_data.phone,
        cnpj=user_data.cnpj,
        company_name=user_data.company_name,
        password_hash=pwd_context.hash(user_data.password),
        active=True
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    logger.info(f"Novo usuário registrado: {user_data.email}")
    
    return new_user

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, session: AsyncSession = Depends(get_db)):
    """Login com email e senha"""
    
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos"
        )
    
    # Verificar senha
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"])
    
    if not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos"
        )
    
    # Gerar JWT token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expire = datetime.utcnow() + access_token_expires
    
    to_encode = {"sub": user.id, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # Atualizar last_login
    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    
    logger.info(f"Usuário fez login: {user_data.email}")
    
    return {"access_token": encoded_jwt, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = None,
    session: AsyncSession = Depends(get_db)
):
    """Obter dados do usuário atual"""
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user
