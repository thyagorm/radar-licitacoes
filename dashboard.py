from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import logging

from ..models import (
    User, MatchedLicitationItem, Portfolio, Licitation, SentAlert
)
from ..utils import get_db
from .portfolio import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/summary")
async def get_summary(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Resumo do dashboard"""
    
    # Total de portfolios
    portfolio_result = await session.execute(
        select(func.count(Portfolio.id)).where(
            Portfolio.user_id == user.id,
            Portfolio.active == True
        )
    )
    total_portfolios = portfolio_result.scalar() or 0
    
    # Total de matches
    matches_result = await session.execute(
        select(func.count(MatchedLicitationItem.id)).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id
        )
    )
    total_matches = matches_result.scalar() or 0
    
    # Matches de hoje
    today = datetime.utcnow().date()
    today_result = await session.execute(
        select(func.count(MatchedLicitationItem.id)).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id,
            MatchedLicitationItem.created_at >= today
        )
    )
    today_matches = today_result.scalar() or 0
    
    # Viabilidade high
    high_result = await session.execute(
        select(func.count(MatchedLicitationItem.id)).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id,
            MatchedLicitationItem.viability == "alta"
        )
    )
    high_viability = high_result.scalar() or 0
    
    # Alertas enviados (últimos 7 dias)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    alerts_result = await session.execute(
        select(func.count(SentAlert.id)).where(
            SentAlert.user_id == user.id,
            SentAlert.sent_at >= seven_days_ago
        )
    )
    recent_alerts = alerts_result.scalar() or 0
    
    return {
        "total_portfolios": total_portfolios,
        "total_matches": total_matches,
        "today_matches": today_matches,
        "high_viability_matches": high_viability,
        "recent_alerts": recent_alerts,
        "company_name": user.company_name,
        "email": user.email
    }

@router.get("/stats")
async def get_stats(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Estatísticas detalhadas"""
    
    # Distribuição por viabilidade
    viability_result = await session.execute(
        select(
            MatchedLicitationItem.viability,
            func.count(MatchedLicitationItem.id)
        ).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id
        ).group_by(MatchedLicitationItem.viability)
    )
    viability_dist = dict(viability_result.all())
    
    # Score médio
    score_result = await session.execute(
        select(func.avg(MatchedLicitationItem.similarity_score)).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id
        )
    )
    avg_score = score_result.scalar() or 0
    
    # Margem média
    margin_result = await session.execute(
        select(func.avg(MatchedLicitationItem.estimated_margin_percent)).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id
        )
    )
    avg_margin = margin_result.scalar() or 0
    
    return {
        "viability_distribution": viability_dist,
        "average_similarity_score": round(float(avg_score), 2),
        "average_margin_percent": round(float(avg_margin), 2) if avg_margin else 0
    }

@router.get("/trends")
async def get_trends(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Tendências dos últimos 30 dias"""
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Matches por dia (últimos 7 dias)
    daily_result = await session.execute(
        select(
            func.date(MatchedLicitationItem.created_at).label("date"),
            func.count(MatchedLicitationItem.id).label("count")
        ).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id,
            MatchedLicitationItem.created_at >= (datetime.utcnow() - timedelta(days=7))
        ).group_by(func.date(MatchedLicitationItem.created_at))
        .order_by(func.date(MatchedLicitationItem.created_at))
    )
    daily_matches = [{"date": str(date), "count": count} for date, count in daily_result.all()]
    
    # Valor total das licitações com match
    value_result = await session.execute(
        select(func.sum(Licitation.estimated_value)).join(
            LicitationItem,
            LicitationItem.licitation_id == Licitation.id
        ).join(
            MatchedLicitationItem,
            MatchedLicitationItem.licitation_item_id == LicitationItem.id
        ).join(
            Portfolio,
            MatchedLicitationItem.portfolio_id == Portfolio.id
        ).where(
            Portfolio.user_id == user.id,
            Licitation.created_at >= thirty_days_ago
        )
    )
    total_value = value_result.scalar() or 0
    
    return {
        "daily_matches": daily_matches,
        "total_opportunity_value": float(total_value),
        "period_days": 30
    }
