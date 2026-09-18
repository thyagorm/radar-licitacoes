from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from ..models import Licitation, User
from ..utils import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class LicitationResponse(BaseModel):
    id: str
    pncp_id: str
    title: str
    modality: str
    org_name: str
    state: str
    estimated_value: float
    publication_date: datetime
    closing_date: Optional[datetime]
    notice_url: Optional[str]
    items_count: int
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[LicitationResponse])
async def list_licitations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    state: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """Listar licitações com filtros opcionais"""
    
    query = select(Licitation)
    
    if state:
        query = query.where(Licitation.state == state.upper())
    
    query = query.order_by(Licitation.publication_date.desc())
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    licitations = result.scalars().all()
    
    return licitations

@router.get("/{licitation_id}", response_model=LicitationResponse)
async def get_licitation(
    licitation_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Obter detalhes de uma licitação"""
    
    licitation = await session.get(Licitation, licitation_id)
    
    if not licitation:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licitação não encontrada"
        )
    
    return licitation

@router.get("/search/")
async def search_licitations(
    q: str = Query(..., min_length=3),
    state: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    session: AsyncSession = Depends(get_db)
):
    """Buscar licitações por texto"""
    
    query = select(Licitation).where(
        Licitation.title.ilike(f"%{q}%")
    )
    
    if state:
        query = query.where(Licitation.state == state.upper())
    
    if min_value:
        query = query.where(Licitation.estimated_value >= min_value)
    
    if max_value:
        query = query.where(Licitation.estimated_value <= max_value)
    
    query = query.limit(50)
    
    result = await session.execute(query)
    licitations = result.scalars().all()
    
    return licitations
