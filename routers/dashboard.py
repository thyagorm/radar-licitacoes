"""
Router de dashboard - Estatísticas e tendências
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from models import (
    User, Portfolio, MatchedLicitationItem, SentAlert,
    Licitation, LicitationItem
)
from utils import get_db
from routers.users import get_current_user

router = APIRouter()


class DashboardSummary(BaseModel):
    """Modelo de resumo do dashboard"""
    total_matches: int
    average_score: float
    total_value: float
    high_viability_count: int
    medium_viability_count: int
    low_viability_count: int
    portfolio_count: int


class StatItem(BaseModel):
    """Modelo de item de estatística"""
    label: str
    value: int


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter resumo do dashboard"""
    
    # Buscar portfolios
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = port_result.scalars().all()
    portfolio_ids = [p.id for p in portfolios]
    
    portfolio_count = len(portfolios)
    
    if not portfolio_ids:
        return {
            "total_matches": 0,
            "average_score": 0.0,
            "total_value": 0.0,
            "high_viability_count": 0,
            "medium_viability_count": 0,
            "low_viability_count": 0,
            "portfolio_count": 0
        }
    
    # Buscar matches
    result = await db.execute(
        select(MatchedLicitationItem).where(
            MatchedLicitationItem.portfolio_id.in_(portfolio_ids)
        )
    )
    matches = result.scalars().all()
    
    total_matches = len(matches)
    average_score = sum(m.similarity_score for m in matches) / total_matches if total_matches > 0 else 0
    
    # Buscar valor total
    total_value = 0
    for match in matches:
        item_result = await db.execute(
            select(LicitationItem).where(LicitationItem.id == match.licitation_item_id)
        )
        item = item_result.scalar_one()
        
        lic_result = await db.execute(
            select(Licitation).where(Licitation.id == item.licitation_id)
        )
        licitation = lic_result.scalar_one()
        
        if licitation.estimated_value:
            total_value += licitation.estimated_value
    
    # Contar por viabilidade
    high = len([m for m in matches if m.viability == "alta"])
    medium = len([m for m in matches if m.viability == "média"])
    low = len([m for m in matches if m.viability == "baixa"])
    
    return {
        "total_matches": total_matches,
        "average_score": round(average_score, 2),
        "total_value": round(total_value, 2),
        "high_viability_count": high,
        "medium_viability_count": medium,
        "low_viability_count": low,
        "portfolio_count": portfolio_count
    }


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter estatísticas detalhadas"""
    
    # Buscar portfolios
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = port_result.scalars().all()
    portfolio_ids = [p.id for p in portfolios]
    
    if not portfolio_ids:
        return {
            "by_viability": [],
            "by_state": [],
            "alerts_sent": 0
        }
    
    # Matches por viabilidade
    result = await db.execute(
        select(MatchedLicitationItem).where(
            MatchedLicitationItem.portfolio_id.in_(portfolio_ids)
        )
    )
    matches = result.scalars().all()
    
    by_viability = [
        {"label": "Alta", "value": len([m for m in matches if m.viability == "alta"])},
        {"label": "Média", "value": len([m for m in matches if m.viability == "média"])},
        {"label": "Baixa", "value": len([m for m in matches if m.viability == "baixa"])}
    ]
    
    # Contar alertas enviados
    alert_result = await db.execute(
        select(func.count(SentAlert.id)).where(SentAlert.user_id == current_user.id)
    )
    alerts_sent = alert_result.scalar() or 0
    
    # Matches por estado
    states = {}
    for match in matches:
        item_result = await db.execute(
            select(LicitationItem).where(LicitationItem.id == match.licitation_item_id)
        )
        item = item_result.scalar_one()
        
        lic_result = await db.execute(
            select(Licitation).where(Licitation.id == item.licitation_id)
        )
        licitation = lic_result.scalar_one()
        
        state = licitation.state or "Desconhecido"
        states[state] = states.get(state, 0) + 1
    
    by_state = [{"label": state, "value": count} for state, count in states.items()]
    
    return {
        "by_viability": by_viability,
        "by_state": by_state,
        "alerts_sent": alerts_sent
    }


@router.get("/trends")
async def get_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter tendências dos últimos N dias"""
    
    # Buscar portfolios
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = port_result.scalars().all()
    portfolio_ids = [p.id for p in portfolios]
    
    if not portfolio_ids:
        return {
            "daily_matches": [],
            "average_daily_score": 0
        }
    
    # Data limite
    limit_date = datetime.utcnow() - timedelta(days=days)
    
    # Matches por dia
    result = await db.execute(
        select(MatchedLicitationItem).where(
            (MatchedLicitationItem.portfolio_id.in_(portfolio_ids)) &
            (MatchedLicitationItem.created_at >= limit_date)
        )
    )
    matches = result.scalars().all()
    
    # Agrupar por dia
    daily_matches = {}
    for match in matches:
        day = match.created_at.date()
        daily_matches[day] = daily_matches.get(day, 0) + 1
    
    # Média diária de score
    average_daily_score = sum(m.similarity_score for m in matches) / len(matches) if matches else 0
    
    return {
        "daily_matches": [
            {"date": str(day), "count": count}
            for day, count in sorted(daily_matches.items())
        ],
        "average_daily_score": round(average_daily_score, 2),
        "total_matches_period": len(matches)
    }


@router.get("/recent-matches")
async def get_recent_matches(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter matches recentes"""
    
    # Buscar portfolios
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == current_user.id)
    )
    portfolios = port_result.scalars().all()
    portfolio_ids = [p.id for p in portfolios]
    
    if not portfolio_ids:
        return []
    
    # Buscar matches recentes
    result = await db.execute(
        select(MatchedLicitationItem)
        .where(MatchedLicitationItem.portfolio_id.in_(portfolio_ids))
        .order_by(MatchedLicitationItem.created_at.desc())
        .limit(limit)
    )
    matches = result.scalars().all()
    
    response = []
    for match in matches:
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
            "match_id": match.id,
            "product_name": portfolio.description,
            "licitation_title": licitation.title,
            "score": match.similarity_score,
            "viability": match.viability,
            "state": licitation.state
        })
    
    return response
