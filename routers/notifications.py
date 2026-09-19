"""
Router de notificações - Histórico e preferências de alertas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models import SentAlert, UserPreference, User
from utils import get_db
from routers.users import get_current_user

router = APIRouter()


class SentAlertResponse(BaseModel):
    """Modelo de resposta de alerta enviado"""
    id: str
    alert_type: str
    whatsapp_status: str = None
    email_status: str = None
    matched_items_count: int
    created_at: datetime


class UserPreferenceCreate(BaseModel):
    """Modelo para criar preferências"""
    states: str = None  # "RJ,SP,MG"
    cities: str = None
    min_value: float = None
    max_value: float = None
    modalities: str = None
    org_types: str = None
    max_daily_alerts: int = 10


class UserPreferenceResponse(BaseModel):
    """Modelo de resposta de preferências"""
    id: str
    states: str = None
    cities: str = None
    min_value: float = None
    max_value: float = None
    modalities: str = None
    org_types: str = None
    max_daily_alerts: int


@router.get("/history", response_model=List[SentAlertResponse])
async def get_alert_history(
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter histórico de alertas enviados"""
    
    result = await db.execute(
        select(SentAlert)
        .where(SentAlert.user_id == current_user.id)
        .order_by(desc(SentAlert.created_at))
        .offset(skip)
        .limit(limit)
    )
    alerts = result.scalars().all()
    
    return [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "whatsapp_status": alert.whatsapp_status,
            "email_status": alert.email_status,
            "matched_items_count": alert.matched_items_count,
            "created_at": alert.created_at
        }
        for alert in alerts
    ]


@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter preferências do usuário"""
    
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferências não configuradas"
        )
    
    return {
        "id": preference.id,
        "states": preference.states,
        "cities": preference.cities,
        "min_value": preference.min_value,
        "max_value": preference.max_value,
        "modalities": preference.modalities,
        "org_types": preference.org_types,
        "max_daily_alerts": preference.max_daily_alerts
    }


@router.post("/preferences", response_model=UserPreferenceResponse)
async def create_preferences(
    pref_data: UserPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Criar preferências do usuário"""
    
    # Verificar se já existe
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferências já existem. Use PUT para atualizar."
        )
    
    preference = UserPreference(
        user_id=current_user.id,
        states=pref_data.states,
        cities=pref_data.cities,
        min_value=pref_data.min_value,
        max_value=pref_data.max_value,
        modalities=pref_data.modalities,
        org_types=pref_data.org_types,
        max_daily_alerts=pref_data.max_daily_alerts
    )
    
    db.add(preference)
    await db.commit()
    await db.refresh(preference)
    
    return {
        "id": preference.id,
        "states": preference.states,
        "cities": preference.cities,
        "min_value": preference.min_value,
        "max_value": preference.max_value,
        "modalities": preference.modalities,
        "org_types": preference.org_types,
        "max_daily_alerts": preference.max_daily_alerts
    }


@router.put("/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    pref_data: UserPreferenceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Atualizar preferências do usuário"""
    
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        # Criar se não existir
        preference = UserPreference(
            user_id=current_user.id,
            states=pref_data.states,
            cities=pref_data.cities,
            min_value=pref_data.min_value,
            max_value=pref_data.max_value,
            modalities=pref_data.modalities,
            org_types=pref_data.org_types,
            max_daily_alerts=pref_data.max_daily_alerts
        )
        db.add(preference)
    else:
        # Atualizar campos
        if pref_data.states is not None:
            preference.states = pref_data.states
        if pref_data.cities is not None:
            preference.cities = pref_data.cities
        if pref_data.min_value is not None:
            preference.min_value = pref_data.min_value
        if pref_data.max_value is not None:
            preference.max_value = pref_data.max_value
        if pref_data.modalities is not None:
            preference.modalities = pref_data.modalities
        if pref_data.org_types is not None:
            preference.org_types = pref_data.org_types
        if pref_data.max_daily_alerts is not None:
            preference.max_daily_alerts = pref_data.max_daily_alerts
    
    await db.commit()
    await db.refresh(preference)
    
    return {
        "id": preference.id,
        "states": preference.states,
        "cities": preference.cities,
        "min_value": preference.min_value,
        "max_value": preference.max_value,
        "modalities": preference.modalities,
        "org_types": preference.org_types,
        "max_daily_alerts": preference.max_daily_alerts
    }


@router.post("/test-whatsapp")
async def test_whatsapp(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enviar mensagem de teste WhatsApp"""
    
    if not current_user.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número WhatsApp não configurado"
        )
    
    # Simular envio (em produção, conectar com WhatsApp API)
    return {
        "status": "test_mode",
        "message": "Modo teste ativado - WhatsApp não configurado",
        "phone": current_user.phone
    }


@router.post("/test-email")
async def test_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enviar mensagem de teste Email"""
    
    # Simular envio (em produção, conectar com SMTP)
    return {
        "status": "test_mode",
        "message": "Modo teste ativado - Email não configurado",
        "email": current_user.email
    }
