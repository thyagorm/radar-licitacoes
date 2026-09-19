"""
Router de matches - Oportunidades encontradas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional

from models import MatchedLicitationItem, User, Portfolio, LicitationItem, Licitation
from utils import get_db
from routers.users import get_current_user

router = APIRouter()


class MatchResponse(BaseModel):
    """Modelo de resposta de match"""
    id: str
    licitation_title: str
    product_name: str
    product_code: str
    similarity_score: float
    estimated_margin_percent: float = None
    viability: str
    licitation_value: float = None
    state: str = None


@router.get("", response_model=List[MatchResponse])
async def list_matches(
    viability: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar matches do usuário"""
    
    # Buscar todos os portfolios do usuário
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = port_result.scalars().all()
    portfolio_ids = [p.id for p in portfolios]
    
    if not portfolio_ids:
        return []
    
    # Buscar matches
    query = select(MatchedLicitationItem).where(
        MatchedLicitationItem.portfolio_id.in_(portfolio_ids)
    ).order_by(desc(MatchedLicitationItem.similarity_score))
    
    # Filtros
    if viability:
        query = query.where(MatchedLicitationItem.viability == viability)
    if min_score:
        query = query.where(MatchedLicitationItem.similarity_score >= min_score)
    
    # Paginação
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    response = []
    for match in matches:
        # Buscar detalhes
        port_result = await db.execute(
            select(Portfolio).where(Portfolio.id == match.portfolio_id)
        )
        portfolio = port_result.scalar_one()
        
        item_result = await db.execute(
            select(LicitationItem).where(LicitationItem.id == match.licitation_item_id)
        )
        item = item_result.scalar_one()
        
        lic_result = await db.execute(
            select(Licitation).where(Licitation.id == item.licitation_id)
        )
        licitation = lic_result.scalar_one()
        
        response.append({
            "id": match.id,
            "licitation_title": licitation.title,
            "product_name": portfolio.description,
            "product_code": portfolio.code,
            "similarity_score": match.similarity_score,
            "estimated_margin_percent": match.estimated_margin_percent,
            "viability": match.viability,
            "licitation_value": licitation.estimated_value,
            "state": licitation.state
        })
    
    return response


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter detalhes de um match"""
    
    result = await db.execute(
        select(MatchedLicitationItem).where(MatchedLicitationItem.id == match_id)
    )
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match não encontrado"
        )
    
    # Verificar permissão
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.id == match.portfolio_id)
    )
    portfolio = port_result.scalar_one()
    
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Buscar detalhes
    item_result = await db.execute(
        select(LicitationItem).where(LicitationItem.id == match.licitation_item_id)
    )
    item = item_result.scalar_one()
    
    lic_result = await db.execute(
        select(Licitation).where(Licitation.id == item.licitation_id)
    )
    licitation = lic_result.scalar_one()
    
    return {
        "id": match.id,
        "licitation_title": licitation.title,
        "product_name": portfolio.description,
        "product_code": portfolio.code,
        "similarity_score": match.similarity_score,
        "estimated_margin_percent": match.estimated_margin_percent,
        "viability": match.viability,
        "licitation_value": licitation.estimated_value,
        "state": licitation.state
    }


@router.get("/stats/summary")
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter resumo de matches"""
    
    # Buscar portfolios
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = port_result.scalars().all()
    portfolio_ids = [p.id for p in portfolios]
    
    if not portfolio_ids:
        return {
            "total_matches": 0,
            "average_score": 0,
            "high_viability": 0,
            "medium_viability": 0,
            "low_viability": 0
        }
    
    # Contar matches
    result = await db.execute(
        select(MatchedLicitationItem).where(
            MatchedLicitationItem.portfolio_id.in_(portfolio_ids)
        )
    )
    matches = result.scalars().all()
    
    total = len(matches)
    average_score = sum(m.similarity_score for m in matches) / total if total > 0 else 0
    
    high = len([m for m in matches if m.viability == "alta"])
    medium = len([m for m in matches if m.viability == "média"])
    low = len([m for m in matches if m.viability == "baixa"])
    
    return {
        "total_matches": total,
        "average_score": round(average_score, 2),
        "high_viability": high,
        "medium_viability": medium,
        "low_viability": low
    }
