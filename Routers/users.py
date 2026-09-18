"""
Router de usuários - Autenticação e gerenciamento de contas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from config import settings
from models import User
from utils import get_db, hash_password, verify_password, create_jwt_token, verify_jwt_token

router = APIRouter()


class UserRegister(BaseModel):
    """Modelo para registro de novo usuário"""
    email: EmailStr
    password: str
    cnpj: str
    company_name: str
    phone: str = None


class UserLogin(BaseModel):
    """Modelo para login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Modelo de resposta do usuário"""
    id: str
    email: str
    company_name: str
    cnpj: str
    phone: str = None
    active: bool


class TokenResponse(BaseModel):
    """Modelo de resposta com token"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


async def get_current_user(
    token: str = None,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependência para obter usuário atual
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido"
        )
    
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return user


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Registrar novo usuário"""
    
    # Verificar se email já existe
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado"
        )
    
    # Verificar se CNPJ já existe
    result = await db.execute(select(User).where(User.cnpj == user_data.cnpj))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já registrado"
        )
    
    # Criar novo usuário
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        cnpj=user_data.cnpj,
        company_name=user_data.company_name,
        phone=user_data.phone,
        active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Gerar token
    access_token = create_jwt_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "company_name": user.company_name,
            "cnpj": user.cnpj,
            "phone": user.phone,
            "active": user.active
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login de usuário"""
    
    # Buscar usuário por email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Verificar senha
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Verificar se ativo
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Gerar token
    access_token = create_jwt_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "company_name": user.company_name,
            "cnpj": user.cnpj,
            "phone": user.phone,
            "active": user.active
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Obter dados do usuário atual"""
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "company_name": current_user.company_name,
        "cnpj": current_user.cnpj,
        "phone": current_user.phone,
        "active": current_user.active
    }