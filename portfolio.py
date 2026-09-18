from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging

from ..models import Portfolio, User
from ..utils import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class PortfolioCreate(BaseModel):
    code: str  # CMED ou NCM
    description: str
    category: str  # "medicamento", "serviço", "produto"
    cost_price: float = None
    min_margin_percent: float = 15.0
    keywords: List[str] = []

class PortfolioUpdate(BaseModel):
    description: str = None
    cost_price: float = None
    min_margin_percent: float = None

class PortfolioResponse(BaseModel):
    id: str
    code: str
    description: str
    category: str
    cost_price: float
    min_margin_percent: float
    keywords: List[str]
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

async def get_current_user(token: str = None, session: AsyncSession = Depends(get_db)):
    """Dependency para validar token e retornar usuário"""
    from jose import jwt, JWTError
    from ..config import settings
    
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

@router.get("/", response_model=List[PortfolioResponse])
async def list_portfolio(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Listar produtos/serviços do usuário"""
    
    result = await session.execute(
        select(Portfolio).where(
            Portfolio.user_id == user.id,
            Portfolio.active == True
        )
    )
    portfolios = result.scalars().all()
    
    return portfolios

@router.post("/", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Adicionar produto/serviço ao portfolio"""
    
    portfolio = Portfolio(
        user_id=user.id,
        code=portfolio_data.code,
        description=portfolio_data.description,
        category=portfolio_data.category,
        cost_price=portfolio_data.cost_price,
        min_margin_percent=portfolio_data.min_margin_percent,
        keywords=portfolio_data.keywords,
        active=True
    )
    
    session.add(portfolio)
    await session.commit()
    await session.refresh(portfolio)
    
    logger.info(f"Portfolio adicionado ao user {user.id}: {portfolio_data.code}")
    
    return portfolio

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    portfolio_data: PortfolioUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Atualizar produto/serviço"""
    
    result = await session.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio não encontrado"
        )
    
    if portfolio_data.description:
        portfolio.description = portfolio_data.description
    if portfolio_data.cost_price is not None:
        portfolio.cost_price = portfolio_data.cost_price
    if portfolio_data.min_margin_percent is not None:
        portfolio.min_margin_percent = portfolio_data.min_margin_percent
    
    portfolio.updated_at = datetime.utcnow()
    session.add(portfolio)
    await session.commit()
    await session.refresh(portfolio)
    
    logger.info(f"Portfolio atualizado: {portfolio_id}")
    
    return portfolio

@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Remover produto/serviço (soft delete)"""
    
    result = await session.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio não encontrado"
        )
    
    portfolio.active = False
    session.add(portfolio)
    await session.commit()
    
    logger.info(f"Portfolio removido: {portfolio_id}")
    
    return {"message": "Portfolio removido com sucesso"}
