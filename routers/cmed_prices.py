"""
Router de mapa de preços CMED
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional

from models import CMEDPrice, User
from utils import get_db
from routers.users import get_current_user

router = APIRouter()


class CMEDPriceResponse(BaseModel):
    """Modelo de resposta de preço CMED"""
    id: str
    code_cmed: str
    description: str
    principio_ativo: str = None
    concentracao: str = None
    forma_farmaceutica: str = None
    price_mg: float = None
    price_unit: float = None


@router.get("", response_model=List[CMEDPriceResponse])
async def list_cmed_prices(
    skip: int = Query(0),
    limit: int = Query(20),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar preços CMED com busca"""
    
    query = select(CMEDPrice)
    
    # Filtro de busca
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            (CMEDPrice.description.ilike(search_term)) |
            (CMEDPrice.code_cmed.ilike(search_term)) |
            (CMEDPrice.principio_ativo.ilike(search_term))
        )
    
    # Paginação
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    prices = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "code_cmed": p.code_cmed,
            "description": p.description,
            "principio_ativo": p.principio_ativo,
            "concentracao": p.concentracao,
            "forma_farmaceutica": p.forma_farmaceutica,
            "price_mg": p.price_mg,
            "price_unit": p.price_unit
        }
        for p in prices
    ]


@router.get("/search")
async def search_cmed(
    code: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Buscar preço por código CMED"""
    
    result = await db.execute(
        select(CMEDPrice).where(CMEDPrice.code_cmed == code.upper())
    )
    price = result.scalar_one_or_none()
    
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código CMED não encontrado"
        )
    
    return {
        "id": price.id,
        "code_cmed": price.code_cmed,
        "description": price.description,
        "principio_ativo": price.principio_ativo,
        "concentracao": price.concentracao,
        "forma_farmaceutica": price.forma_farmaceutica,
        "price_mg": price.price_mg,
        "price_unit": price.price_unit
    }


@router.get("/by-description")
async def search_by_description(
    query: str = Query(...),
    limit: int = Query(10),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Buscar por descrição/nome do medicamento"""
    
    search_term = f"%{query.lower()}%"
    
    result = await db.execute(
        select(CMEDPrice)
        .where(CMEDPrice.description.ilike(search_term))
        .limit(limit)
    )
    prices = result.scalars().all()
    
    if not prices:
        return []
    
    return [
        {
            "id": p.id,
            "code_cmed": p.code_cmed,
            "description": p.description,
            "principio_ativo": p.principio_ativo,
            "concentracao": p.concentracao,
            "forma_farmaceutica": p.forma_farmaceutica,
            "price_mg": p.price_mg,
            "price_unit": p.price_unit
        }
        for p in prices
    ]


@router.get("/compare")
async def compare_prices(
    codes: str = Query(...),  # "05.2.2.1,05.2.2.2"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Comparar preços de múltiplos medicamentos"""
    
    code_list = [c.strip() for c in codes.split(",")]
    
    result = await db.execute(
        select(CMEDPrice).where(CMEDPrice.code_cmed.in_(code_list))
    )
    prices = result.scalars().all()
    
    if not prices:
        return []
    
    # Ordenar por preço
    sorted_prices = sorted(prices, key=lambda p: p.price_unit or 0)
    
    return [
        {
            "id": p.id,
            "code_cmed": p.code_cmed,
            "description": p.description,
            "principio_ativo": p.principio_ativo,
            "concentracao": p.concentracao,
            "price_mg": p.price_mg,
            "price_unit": p.price_unit
        }
        for p in sorted_prices
    ]


@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar categorias disponíveis (formas farmacêuticas)"""
    
    result = await db.execute(
        select(CMEDPrice.forma_farmaceutica.distinct())
    )
    categories = result.scalars().all()
    
    return {
        "categories": [c for c in categories if c]
    }


@router.get("/by-category")
async def search_by_category(
    category: str = Query(...),  # "comprimido", "injetável", etc
    limit: int = Query(20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar medicamentos por forma farmacêutica"""
    
    result = await db.execute(
        select(CMEDPrice)
        .where(CMEDPrice.forma_farmaceutica.ilike(f"%{category}%"))
        .limit(limit)
    )
    prices = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "code_cmed": p.code_cmed,
            "description": p.description,
            "principio_ativo": p.principio_ativo,
            "concentracao": p.concentracao,
            "forma_farmaceutica": p.forma_farmaceutica,
            "price_mg": p.price_mg,
            "price_unit": p.price_unit
        }
        for p in prices
    ]


@router.post("/populate-sample")
async def populate_sample_prices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Preencher com dados de amostra (desenvolvimento)"""
    
    sample_data = [
        CMEDPrice(
            code_cmed="05.2.2.1",
            description="Amoxicilina 500mg",
            principio_ativo="Amoxicilina",
            concentracao="500mg",
            forma_farmaceutica="Comprimido",
            price_mg=0.005,
            price_unit=2.50
        ),
        CMEDPrice(
            code_cmed="05.2.2.2",
            description="Amoxicilina 250mg",
            principio_ativo="Amoxicilina",
            concentracao="250mg",
            forma_farmaceutica="Comprimido",
            price_mg=0.003,
            price_unit=1.80
        ),
        CMEDPrice(
            code_cmed="05.2.1.1",
            description="Penicilina G Procaína 400.000 UI",
            principio_ativo="Penicilina G Procaína",
            concentracao="400.000 UI",
            forma_farmaceutica="Injetável",
            price_mg=0.001,
            price_unit=5.00
        ),
        CMEDPrice(
            code_cmed="05.2.3.1",
            description="Cefalexina 500mg",
            principio_ativo="Cefalexina",
            concentracao="500mg",
            forma_farmaceutica="Comprimido",
            price_mg=0.006,
            price_unit=3.20
        ),
        CMEDPrice(
            code_cmed="05.2.4.1",
            description="Azitromicina 500mg",
            principio_ativo="Azitromicina",
            concentracao="500mg",
            forma_farmaceutica="Comprimido",
            price_mg=0.008,
            price_unit=8.50
        ),
    ]
    
    for item in sample_data:
        db.add(item)
    
    await db.commit()
    
    return {
        "message": "Dados de amostra inseridos com sucesso",
        "count": len(sample_data)
    }
