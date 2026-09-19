from fastapi import APIRouter
from datetime import datetime, date
import json
from services.pncp_client import get_conn

router = APIRouter(prefix="/api/dashboard-stats", tags=["Dashboard Executivo"])

@router.get("")
async def obter_estatisticas_completas():
    conn = get_conn()
    cursor = conn.cursor()

    # 1. Dados da Mesa de Operação
    cursor.execute("SELECT status, valor_estimado, proposta_valor, motivo_perda FROM processos_licitatorios")
    linhas_mesa = cursor.fetchall()

    total_ativas = sum(1 for r in linhas_mesa if r[0] == 'ATIVA')
    total_analise = sum(1 for r in linhas_mesa if r[0] == 'EM_ANALISE')
    total_ganhas = sum(1 for r in linhas_mesa if r[0] == 'GANHA')
    total_perdidas = sum(1 for r in linhas_mesa if r[0] == 'PERDIDA')
    total_descartadas = sum(1 for r in linhas_mesa if r[0] == 'DESCARTADA')

    soma_propostas = sum(float(r[2] or 0.0) for r in linhas_mesa if r[0] in ['EM_ANALISE', 'GANHA'])
    soma_ganho = sum(float(r[2] or 0.0) for r in linhas_mesa if r[0] == 'GANHA')

    total_finalizadas = total_ganhas + total_perdidas
    win_rate = round((total_ganhas / total_finalizadas * 100), 1) if total_finalizadas > 0 else 0.0

    # Motivos de Perda
    motivos_contagem = {}
    for r in linhas_mesa:
        if r[0] == 'PERDIDA':
            motivo = r[3] or "Não informado"
            motivo_curto = motivo.split('(')[0].strip() if '(' in motivo else motivo
            motivos_contagem[motivo_curto] = motivos_contagem.get(motivo_curto, 0) + 1

    # 2. Total de Matches
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='matches'")
    tem_matches = cursor.fetchone()[0]
    total_matches = 0
    if tem_matches:
        cursor.execute("SELECT COUNT(*) FROM matches WHERE score >= 50")
        total_matches = cursor.fetchone()[0]
    if total_matches == 0:
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='licitacoes_pncp'")
        if cursor.fetchone()[0]:
            cursor.execute("SELECT COUNT(*) FROM licitacoes_pncp")
            total_matches = cursor.fetchone()[0]

    # 3. Alertas de Certidões (Empresa)
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dados_empresa'")
    certidoes_risco = 0
    if cursor.fetchone()[0]:
        cursor.execute("SELECT val_cnd_federal, val_crf_fgts, val_cndt_trabalhista, val_cnd_estadual, val_cnd_municipal, outros_documentos_json FROM dados_empresa WHERE id = 1")
        row_emp = cursor.fetchone()
        if row_emp:
            datas = [row_emp[0], row_emp[1], row_emp[2], row_emp[3], row_emp[4]]
            try:
                outros = json.loads(row_emp[5] or "[]")
                for o in outros:
                    if o.get("validade"):
                        datas.append(o["validade"])
            except:
                pass

            hoje = date.today()
            for d_str in datas:
                if d_str:
                    try:
                        d_obj = datetime.strptime(d_str[:10], "%Y-%m-%d").date()
                        dias = (d_obj - hoje).days
                        if dias <= 15:
                            certidoes_risco += 1
                    except:
                        pass

    # 4. Próximos Pregões / Aberturas
    cursor.execute("""
        SELECT id, numero_edital, orgao_nome, uf, objeto, valor_estimado, data_abertura, status 
        FROM processos_licitatorios 
        WHERE status IN ('ATIVA', 'EM_ANALISE') 
        ORDER BY id DESC LIMIT 5
    """)
    proximos = []
    for r in cursor.fetchall():
        proximos.append({
            "id": r[0],
            "numero_edital": r[1],
            "orgao_nome": r[2],
            "uf": r[3],
            "objeto": r[4],
            "valor_estimado": float(r[5] or 0.0),
            "data_abertura": r[6] or "A definir",
            "status": r[7]
        })

    conn.close()

    return {
        "kpis": {
            "em_operacao": total_ativas + total_analise,
            "ativas": total_ativas,
            "em_analise": total_analise,
            "ganhas": total_ganhas,
            "perdidas": total_perdidas,
            "win_rate": win_rate,
            "total_propostas": soma_propostas,
            "total_ganho": soma_ganho,
            "total_matches": total_matches,
            "certidoes_risco": certidoes_risco
        },
        "motivos_perda": motivos_contagem,
        "proximos_pregoes": proximos
    }
