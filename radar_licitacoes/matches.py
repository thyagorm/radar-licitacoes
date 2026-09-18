from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging

from ..models import MatchedLicitationItem, User, LicitationItem, Licitation, Portfolio
from ..utils import get_db
from .portfolio import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class MatchResponse(BaseModel):
    id: str
    similarity_score: float
    match_reason: str
    estimated_margin_percent: float
    viability: str
    licitation_title: str
    org_name: str
    estimated_value: float
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[MatchResponse])
async def list_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    viability: str = Query(None),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Listar matches do usuário"""
    
    # Subquery para portfolios do usuário
    user_portfolios = select(Portfolio.id).where(
        Portfolio.user_id == user.id
    )
    
    query = select(MatchedLicitationItem).join(
        Portfolio,
        MatchedLicitationItem.portfolio_id == Portfolio.id
    ).join(
        LicitationItem,
        MatchedLicitationItem.licitation_item_id == LicitationItem.id
    ).join(
        Licitation,
        LicitationItem.licitation_id == Licitation.id
    ).where(
        Portfolio.user_id == user.id
    )
    
    if viability:
        query = query.where(MatchedLicitationItem.viability == viability)
    
    query = query.order_by(MatchedLicitationItem.similarity_score.desc())
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    matches = result.scalars().all()
    
    # Formatar resposta
    response = []
    for match in matches:
        item = await session.get(LicitationItem, match.licitation_item_id)
        licitation = await session.get(Licitation, item.licitation_id)
        
        response.append(MatchResponse(
            id=match.id,
            similarity_score=match.similarity_score,
            match_reason=match.match_reason,
            estimated_margin_percent=match.estimated_margin_percent,
            viability=match.viability,
            licitation_title=licitation.title,
            org_name=licitation.org_name,
            estimated_value=licitation.estimated_value,
            created_at=match.created_at
        ))
    
    return response

@router.get("/{match_id}")
async def get_match(
    match_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Obter detalhes de um match"""
    
    match = await session.get(MatchedLicitationItem, match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match não encontrado"
        )
    
    # Verificar autorização
    portfolio = await session.get(Portfolio, match.portfolio_id)
    if portfolio.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    item = await session.get(LicitationItem, match.licitation_item_id)
    licitation = await session.get(Licitation, item.licitation_id)
    
    return {
        "match": match,
        "item": item,
        "licitation": licitation
    }
