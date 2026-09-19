from fastapi import APIRouter, Query
from typing import Optional
from services.pncp_client import (
    consultar_editais_pncp,
    persistir_editais_pncp,
    get_conn
)

router = APIRouter()

@router.get("/licitacoes")
async def obter_licitacoes_pncp(
    busca: Optional[str] = Query(None),
    uf: Optional[str] = Query(None),
    orgao: Optional[str] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    data_abertura_ini: Optional[str] = Query(None)
):
    conn = get_conn()
    cursor = conn.cursor()
    query = "SELECT * FROM licitacoes_pncp WHERE 1=1"
    params = []

    if busca:
        query += " AND (objeto LIKE ? OR segmento LIKE ?)"
        termo = f"%{busca}%"
        params.extend([termo, termo])

    if uf:
        query += " AND uf = ?"
        params.append(uf.upper())

    if orgao:
        query += " AND orgao_nome LIKE ?"
        params.append(f"%{orgao}%")

    if valor_min is not None:
        query += " AND valor_estimado >= ?"
        params.append(valor_min)

    if valor_max is not None:
        query += " AND valor_estimado <= ?"
        params.append(valor_max)

    if data_abertura_ini:
        query += " AND data_abertura_proposta >= ?"
        params.append(data_abertura_ini)

    query += " ORDER BY id DESC LIMIT 150"
    cursor.execute(query, params)
    itens = [dict(r) for r in cursor.fetchall()]
    conn.close()

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
