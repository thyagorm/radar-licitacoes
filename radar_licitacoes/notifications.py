from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List
from datetime import datetime
import logging

from ..models import SentAlert, UserPreference, User
from ..utils import get_db
from .portfolio import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class UserPreferenceUpdate(BaseModel):
    states: List[str] = []
    cities: List[str] = []
    min_value: float = 1000.0
    max_value: float = None
    modalities: List[str] = []
    org_types: List[str] = []
    max_alerts_per_week: int = 10

class SentAlertResponse(BaseModel):
    id: str
    alert_type: str
    whatsapp_status: str
    email_status: str
    matched_items_count: int
    sent_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/history", response_model=List[SentAlertResponse])
async def get_alert_history(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Histórico de alertas enviados"""
    
    result = await session.execute(
        select(SentAlert)
        .where(SentAlert.user_id == user.id)
        .order_by(desc(SentAlert.sent_at))
        .limit(50)
    )
    alerts = result.scalars().all()
    
    return alerts

@router.get("/preferences")
async def get_preferences(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Obter preferências de notificação"""
    
    result = await session.execute(
        select(UserPreference).where(
            UserPreference.user_id == user.id
        )
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        # Criar preferências padrão
        preference = UserPreference(
            user_id=user.id,
            states=[],
            cities=[],
            min_value=1000.0,
            modalities=[],
            org_types=[]
        )
        session.add(preference)
        await session.commit()
    
    return preference

@router.put("/preferences")
async def update_preferences(
    prefs: UserPreferenceUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Atualizar preferências de notificação"""
    
    result = await session.execute(
        select(UserPreference).where(
            UserPreference.user_id == user.id
        )
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        preference = UserPreference(user_id=user.id)
    
    preference.states = prefs.states
    preference.cities = prefs.cities
    preference.min_value = prefs.min_value
    preference.max_value = prefs.max_value
    preference.modalities = prefs.modalities
    preference.org_types = prefs.org_types
    preference.max_alerts_per_week = prefs.max_alerts_per_week
    
    session.add(preference)
    await session.commit()
    
    logger.info(f"Preferências atualizadas para user {user.id}")
    
    return {"message": "Preferências atualizadas com sucesso"}

@router.post("/test-whatsapp")
async def test_whatsapp(
    user: User = Depends(get_current_user)
):
    """Testar envio WhatsApp"""
    
    if not user.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum número de WhatsApp cadastrado"
        )
    
    return {
        "status": "success",
        "message": "WhatsApp de teste enviado",
        "phone": user.phone
    }

@router.post("/test-email")
async def test_email(
    user: User = Depends(get_current_user)
):
    """Testar envio de email"""
    
    return {
        "status": "success",
        "message": "Email de teste será enviado",
        "email": user.email
    }
