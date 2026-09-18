"""
Router de licitações - Buscar licitações públicas
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models import Licitation, LicitationItem, User
from utils import get_db
from routers.users import get_current_user

router = APIRouter()


class LicitationItemResponse(BaseModel):
    """Modelo de resposta de item"""
    id: str
    item_number: int
    description: str
    quantity: float = None
    unit: str = None
    code_cmed: str = None
    code_ncm: str = None


class LicitationResponse(BaseModel):
    """Modelo de resposta de licitação"""
    id: str
    pncp_id: str
    title: str
    modality: str = None
    org_name: str
    state: str
    publication_date: datetime = None
    closing_date: datetime = None
    estimated_value: float = None
    notice_url: str = None
    items: List[LicitationItemResponse] = []


@router.get("", response_model=List[LicitationResponse])
async def list_licitations(
    state: Optional[str] = Query(None),
    min_value: Optional[float] = Query(None),
    max_value: Optional[float] = Query(None),
    modality: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar licitações com filtros"""
    
    query = select(Licitation).order_by(desc(Licitation.publication_date))
    
    # Filtros
    if state:
        query = query.where(Licitation.state == state.upper())
    if min_value:
        query = query.where(Licitation.estimated_value >= min_value)
    if max_value:
        query = query.where(Licitation.estimated_value <= max_value)
    if modality:
        query = query.where(Licitation.modality.ilike(f"%{modality}%"))
    
    # Paginação
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    licitations = result.scalars().all()
    
    response = []
    for lic in licitations:
        # Buscar items
        items_result = await db.execute(
            select(LicitationItem).where(LicitationItem.licitation_id == lic.id)
        )
        items = items_result.scalars().all()
        
        response.append({
            "id": lic.id,
            "pncp_id": lic.pncp_id,
            "title": lic.title,
            "modality": lic.modality,
            "org_name": lic.org_name,
            "state": lic.state,
            "publication_date": lic.publication_date,
            "closing_date": lic.closing_date,
            "estimated_value": lic.estimated_value,
            "notice_url": lic.notice_url,
            "items": [
                {
                    "id": item.id,
                    "item_number": item.item_number,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "code_cmed": item.code_cmed,
                    "code_ncm": item.code_ncm
                }
                for item in items
            ]
        })
    
    return response


@router.get("/{licitation_id}", response_model=LicitationResponse)
async def get_licitation(
    licitation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obter detalhes de uma licitação"""
    
    result = await db.execute(
        select(Licitation).where(Licitation.id == licitation_id)
    )
    licitation = result.scalar_one_or_none()
    
    if not licitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licitação não encontrada"
        )
    
    # Buscar items
    items_result = await db.execute(
        select(LicitationItem).where(LicitationItem.licitation_id == licitation.id)
    )
    items = items_result.scalars().all()
    
    return {
        "id": licitation.id,
        "pncp_id": licitation.pncp_id,
        "title": licitation.title,
        "modality": licitation.modality,
        "org_name": licitation.org_name,
        "state": licitation.state,
        "publication_date": licitation.publication_date,
        "closing_date": licitation.closing_date,
        "estimated_value": licitation.estimated_value,
        "notice_url": licitation.notice_url,
        "items": [
            {
                "id": item.id,
                "item_number": item.item_number,
                "description": item.description,
                "quantity": item.quantity,
                "unit": item.unit,
                "code_cmed": item.code_cmed,
                "code_ncm": item.code_ncm
            }
            for item in items
        ]
    }


@router.get("/search/by-code")
async def search_by_code(
    code: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Buscar licitações por código CMED/NCM"""
    
    result = await db.execute(
        select(LicitationItem).where(
            (LicitationItem.code_cmed == code) | (LicitationItem.code_ncm == code)
        )
    )
    items = result.scalars().all()
    
    if not items:
        return []
    
    # Buscar licitações correspondentes
    licitation_ids = [item.licitation_id for item in items]
    lic_result = await db.execute(
        select(Licitation).where(Licitation.id.in_(licitation_ids))
    )
    licitations = lic_result.scalars().all()
    
    response = []
    for lic in licitations:
        items_result = await db.execute(
            select(LicitationItem).where(LicitationItem.licitation_id == lic.id)
        )
        lic_items = items_result.scalars().all()
        
        response.append({
            "id": lic.id,
            "pncp_id": lic.pncp_id,
            "title": lic.title,
            "modality": lic.modality,
            "org_name": lic.org_name,
            "state": lic.state,
            "publication_date": lic.publication_date,
            "closing_date": lic.closing_date,
            "estimated_value": lic.estimated_value,
            "notice_url": lic.notice_url,
            "items": [
                {
                    "id": item.id,
                    "item_number": item.item_number,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "code_cmed": item.code_cmed,
                    "code_ncm": item.code_ncm
                }
                for item in lic_items
            ]
        })
    
    return response