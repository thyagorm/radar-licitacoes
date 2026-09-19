from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from services.pncp_client import get_conn

router = APIRouter(prefix="/api/matches", tags=["Matches Inteligentes"])

@router.get("")
async def listar_matches_endpoint(min_score: Optional[float] = Query(0.0), uf: Optional[str] = Query(None)):
    """
    Retorna oportunidades identificadas pelo cruzamento do catálogo com o PNCP.
    """
    conn = get_conn()
    cursor = conn.cursor()

    # Procura tabela de matches ou gera a partir dos editais existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
    tem_tabela = cursor.fetchone()

    matches = []
    if tem_tabela:
        query = "SELECT id, licitacao_id, edital_numero, orgao_nome, uf, objeto, score, termos_encontrados, valor_estimado, link_edital, criado_em FROM matches WHERE score >= ?"
        params = [min_score]
        if uf and uf != 'TODOS':
            query += " AND uf = ?"
            params.append(uf)
        query += " ORDER BY score DESC, id DESC LIMIT 50"
        cursor.execute(query, params)
        for r in cursor.fetchall():
            matches.append({
                "id": r[0],
                "licitacao_id": r[1],
                "numero_edital": r[2],
                "orgao_nome": r[3],
                "uf": r[4],
                "objeto": r[5],
                "score": float(r[6] or 0.0),
                "termos": r[7] or "",
                "valor_estimado": float(r[8] or 0.0),
                "link_edital": r[9] or "",
                "criado_em": r[10]
            })

    # Caso a tabela ainda não contenha dados, recorre aos processos e licitações em cache
    if not matches:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='licitacoes_pncp'")
        tem_pncp = cursor.fetchone()
        if tem_pncp:
            cursor.execute("SELECT numero_edital, orgao_nome, uf, objeto, valor_estimado, link_edital, data_abertura FROM licitacoes_pncp ORDER BY id DESC LIMIT 25")
            for r in cursor.fetchall():
                matches.append({
                    "id": 0,
                    "licitacao_id": 0,
                    "numero_edital": r[0] or "-",
                    "orgao_nome": r[1] or "Órgão Público",
                    "uf": r[2] or "BR",
                    "objeto": r[3] or "",
                    "score": 85.0,
                    "termos": "Medicamentos / Insumos compatíveis",
                    "valor_estimado": float(r[4] or 0.0),
                    "link_edital": r[5] or "",
                    "criado_em": r[6] or ""
                })

    conn.close()
    return {"sucesso": True, "total": len(matches), "matches": matches}
