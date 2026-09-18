"""
Router de portfolio - Gerenciar produtos/serviços
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List

from models import Portfolio, User
from utils import get_db
from routers.users import get_current_user

router = APIRouter()


class PortfolioCreate(BaseModel):
    """Modelo para criar portfolio"""
    code: str  # CMED ou NCM
    description: str
    category: str = None
    cost_price: float
    min_margin_percent: float = 20.0
    keywords: str = None


class PortfolioUpdate(BaseModel):
    """Modelo para atualizar portfolio"""
    description: str = None
    category: str = None
    cost_price: float = None
    min_margin_percent: float = None
    keywords: str = None


class PortfolioResponse(BaseModel):
    """Modelo de resposta do portfolio"""
    id: str
    code: str
    description: str
    category: str = None
    cost_price: float
    min_margin_percent: float
    keywords: str = None


@router.get("", response_model=List[PortfolioResponse])
async def list_portfolios(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar produtos do usuário"""
    
    result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "code": p.code,
            "description": p.description,
            "category": p.category,
            "cost_price": p.cost_price,
            "min_margin_percent": p.min_margin_percent,
            "keywords": p.keywords
        }
        for p in portfolios
    ]


@router.post("", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Criar novo produto"""
    
    portfolio = Portfolio(
        user_id=current_user.id,
        code=portfolio_data.code,
        description=portfolio_data.description,
        category=portfolio_data.category,
        cost_price=portfolio_data.cost_price,
        min_margin_percent=portfolio_data.min_margin_percent,
        keywords=portfolio_data.keywords
    )
    
    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)
    
    return {
        "id": portfolio.id,
        "code": portfolio.code,
        "description": portfolio.description,
        "category": portfolio.category,
        "cost_price": portfolio.cost_price,
        "min_margin_percent": portfolio.min_margin_percent,
        "keywords": portfolio.keywords
    }


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter detalhes de um produto"""
    
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    return {
        "id": portfolio.id,
        "code": portfolio.code,
        "description": portfolio.description,
        "category": portfolio.category,
        "cost_price": portfolio.cost_price,
        "min_margin_percent": portfolio.min_margin_percent,
        "keywords": portfolio.keywords
    }


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    portfolio_data: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualizar produto"""
    
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    # Atualizar campos
    update_data = portfolio_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(portfolio, key, value)
    
    await db.commit()
    await db.refresh(portfolio)
    
    return {
        "id": portfolio.id,
        "code": portfolio.code,
        "description": portfolio.description,
        "category": portfolio.category,
        "cost_price": portfolio.cost_price,
        "min_margin_percent": portfolio.min_margin_percent,
        "keywords": portfolio.keywords
    }


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remover produto"""
    
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id
        )
    )
    portfolio = result.scalar_one_or_none()
    
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    await db.delete(portfolio)
    await db.commit()
    
    return {"message": "Produto removido com sucesso"}