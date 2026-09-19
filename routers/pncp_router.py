from fastapi import APIRouter, Query
from typing import Optional
from services.pncp_client import (
    consultar_editais_pncp,
    persistir_editais_pncp,
    listar_editais_pncp_banco
)

router = APIRouter()

@router.get("/licitacoes")
async def obter_licitacoes_pncp(busca: Optional[str] = Query(None), uf: Optional[str] = Query(None)):
    itens = listar_editais_pncp_banco(limite=100, busca=busca, uf=uf)
    return {
        "total": len(itens),
        "licitacoes": itens
    }

@router.post("/sincronizar")
async def sincronizar_pncp(segmento: Optional[str] = Query(None)):
    editais = consultar_editais_pncp(termo_busca=segmento, dias_atras=2, limite_por_uf=20)
    novos = persistir_editais_pncp(editais)
    return {
        "sucesso": True,
        "total_recebidos": len(editais),
        "novos_inseridos": novos,
        "segmento_buscado": segmento if segmento else "Todos os segmentos",
        "mensagem": f"{novos} novos editais sincronizados."
    }
