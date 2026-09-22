from services.sequencial_service import gerar_proximo_codigo_interno
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from services.pncp_client import get_conn

def inicializar_tabela_processos():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processos_licitatorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origem TEXT DEFAULT 'PNCP',
            numero_edital TEXT NOT NULL,
            orgao_nome TEXT NOT NULL,
            uf TEXT DEFAULT 'BR',
            objeto TEXT NOT NULL,
            segmento TEXT DEFAULT 'MEDICAMENTOS',
            valor_estimado REAL DEFAULT 0.0,
            data_abertura TEXT,
            link_edital TEXT,
            status TEXT DEFAULT 'ATIVA',
            viabilidade TEXT DEFAULT 'PENDENTE',
            score REAL DEFAULT 0.0,
            proposta_valor REAL DEFAULT 0.0,
            lance_minimo REAL DEFAULT 0.0,
            resultado TEXT DEFAULT 'PENDENTE',
            resultado_data TEXT,
            motivo_perda TEXT DEFAULT '',
            notas TEXT DEFAULT '',
            itens_json TEXT DEFAULT '[]',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migração segura para garantir a coluna motivo_perda se a tabela já existia
    cursor.execute("PRAGMA table_info(processos_licitatorios)")
    colunas_db = [c[1] for c in cursor.fetchall()]
    if "motivo_perda" not in colunas_db:
        cursor.execute("ALTER TABLE processos_licitatorios ADD COLUMN motivo_perda TEXT DEFAULT ''")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_custos_produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            termo_chave TEXT UNIQUE,
            codigo_cmed TEXT,
            ultimo_custo REAL NOT NULL,
            ultima_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def obter_custo_historico(termo: str) -> Optional[float]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT ultimo_custo FROM historico_custos_produtos WHERE termo_chave = ?", (termo.strip().lower(),))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

def salvar_custo_historico(termo: str, custo: float, codigo_cmed: Optional[str] = None):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historico_custos_produtos (termo_chave, codigo_cmed, ultimo_custo, ultima_atualizacao)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(termo_chave) DO UPDATE SET
            ultimo_custo = excluded.ultimo_custo,
            codigo_cmed = COALESCE(excluded.codigo_cmed, historico_custos_produtos.codigo_cmed),
            ultima_atualizacao = CURRENT_TIMESTAMP
    ''', (termo.strip().lower(), codigo_cmed, custo))
    conn.commit()
    conn.close()

def promover_edital_pncp(dados: Dict[str, Any]) -> Dict[str, Any]:
    inicializar_tabela_processos()
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM processos_licitatorios WHERE numero_edital = ? AND orgao_nome = ?",
        (dados.get("numero_edital", "-"), dados.get("orgao_nome", ""))
    )
    existente = cursor.fetchone()
    if existente:
        conn.close()
        return {"sucesso": False, "mensagem": "Este edital já está na sua Mesa de Operação!", "id": existente[0]}

    empresa_id = dados.get("empresa_id", 1)
    ano, sequencial, codigo_interno = gerar_proximo_codigo_interno(empresa_id=empresa_id)

    cursor.execute('''
        INSERT INTO processos_licitatorios 
        (origem, numero_edital, orgao_nome, uf, objeto, segmento, valor_estimado, data_abertura, link_edital, status, viabilidade, empresa_id, ano, sequencial, codigo_interno)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ATIVA', 'PENDENTE', ?, ?, ?, ?)
    ''', (
        'PNCP',
        dados.get("numero_edital", "-"),
        dados.get("orgao_nome", "Órgão Público"),
        dados.get("uf", "BR"),
        dados.get("objeto", ""),
        dados.get("segmento", "MEDICAMENTOS"),
        float(dados.get("valor_estimado") or 0.0),
        dados.get("data_abertura", ""),
        dados.get("link_edital", ""),
        empresa_id,
        ano,
        sequencial,
        codigo_interno
    ))
    novo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"sucesso": True, "mensagem": "Edital adicionado com sucesso às Ativas da Mesa!", "id": novo_id}

def cadastrar_processo_manual(dados: Dict[str, Any]) -> Dict[str, Any]:
    inicializar_tabela_processos()
    conn = get_conn()
    cursor = conn.cursor()

    empresa_id = dados.get("empresa_id", 1)
    ano, sequencial, codigo_interno = gerar_proximo_codigo_interno(empresa_id=empresa_id)

    cursor.execute('''
        INSERT INTO processos_licitatorios 
        (origem, numero_edital, orgao_nome, uf, objeto, segmento, valor_estimado, data_abertura, link_edital, status, viabilidade, notas, empresa_id, ano, sequencial, codigo_interno)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ATIVA', 'PENDENTE', ?, ?, ?, ?, ?)
    ''', (
        'MANUAL',
        dados.get("numero_edital", "-"),
        dados.get("orgao_nome", "Órgão Licitante"),
        dados.get("uf", "BR"),
        dados.get("objeto", ""),
        dados.get("segmento", "MEDICAMENTOS"),
        float(dados.get("valor_estimado") or 0.0),
        dados.get("data_abertura", ""),
        dados.get("link_edital", ""),
        dados.get("notas", ""),
        empresa_id,
        ano,
        sequencial,
        codigo_interno
    ))
    novo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"sucesso": True, "mensagem": "Processo manual criado nas Ativas da Mesa!", "id": novo_id}

def obter_detalhes_processo(processo_id: int) -> Optional[Dict[str, Any]]:
    inicializar_tabela_processos()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM processos_licitatorios WHERE id = ?", (processo_id,))
    linha = cursor.fetchone()

    if not linha:
        conn.close()
        return None

    colunas = [c[0] for c in cursor.description]
    dados = dict(zip(colunas, linha))
    conn.close()

    itens_brutos = dados.get("itens_json")
    if itens_brutos and isinstance(itens_brutos, str):
        try:
            dados["itens"] = json.loads(itens_brutos)
        except Exception:
            dados["itens"] = []
    else:
        dados["itens"] = []

    dados["valor_estimado"] = float(dados.get("valor_estimado") or 0.0)
    dados["proposta_valor"] = float(dados.get("proposta_valor") or 0.0)
    dados["lance_minimo"] = float(dados.get("lance_minimo") or 0.0)
    return dados

def salvar_proposta_processo(processo_id: int, itens_com_custo: List[Dict[str, Any]], valor_total_proposta: float, lance_minimo: float, notas: str) -> bool:
    conn = get_conn()
    cursor = conn.cursor()

    for item in itens_com_custo:
        nome_prod = item.get("nome", "").strip()
        custo = float(item.get("custo_unitario") or 0.0)
        cmed = item.get("codigo_cmed")
        if nome_prod and custo > 0:
            salvar_custo_historico(nome_prod, custo, cmed)

    custo_total = sum(float(i.get("custo_unitario") or 0.0) * float(i.get("quantidade") or 1) for i in itens_com_custo)
    viabilidade = 'PENDENTE'
    if custo_total > 0 and valor_total_proposta > 0:
        margem = ((valor_total_proposta - custo_total) / valor_total_proposta) * 100
        if margem >= 30:
            viabilidade = 'ALTO'
        elif margem >= 20:
            viabilidade = 'MEDIO'
        else:
            viabilidade = 'BAIXO'

    cursor.execute('''
        UPDATE processos_licitatorios SET
            status = 'EM_ANALISE',
            proposta_valor = ?,
            lance_minimo = ?,
            viabilidade = ?,
            notas = ?,
            itens_json = ?,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        valor_total_proposta,
        lance_minimo,
        viabilidade,
        notas,
        json.dumps(itens_com_custo, ensure_ascii=False),
        processo_id
    ))
    conn.commit()
    conn.close()
    return True

def registrar_resultado_processo(processo_id: int, resultado: str, motivo_perda: str = "", notas_adicionais: str = "") -> bool:
    status_final = 'GANHA' if resultado == 'GANHOU' else ('PERDIDA' if resultado == 'PERDEU' else 'DESCARTADA')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE processos_licitatorios SET
            status = ?,
            resultado = ?,
            motivo_perda = ?,
            resultado_data = CURRENT_TIMESTAMP,
            notas = CASE WHEN ? != '' THEN notas || '\nNota: ' || ? ELSE notas END,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status_final, resultado, motivo_perda, notas_adicionais, notas_adicionais, processo_id))
    conn.commit()
    conn.close()
    return True

def descartar_processo(processo_id: int) -> bool:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE processos_licitatorios SET status = 'DESCARTADA', atualizado_em = CURRENT_TIMESTAMP WHERE id = ?", (processo_id,))
    conn.commit()
    conn.close()
    return True

def listar_processos_operacao(status_filtro: Optional[str] = None) -> Dict[str, Any]:
    inicializar_tabela_processos()
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT status, COUNT(*) FROM processos_licitatorios GROUP BY status")
    contagens = dict(cursor.fetchall())
    
    query = "SELECT * FROM processos_licitatorios"
    params = []

    if status_filtro and status_filtro != 'TODOS':
        query += " WHERE status = ?"
        params.append(status_filtro)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    linhas = cursor.fetchall()
    colunas = [c[0] for c in cursor.description]
    conn.close()

    processos = []
    for r in linhas:
        p = dict(zip(colunas, r))
        processos.append(p)

    return {
        "contagens": {
            "ATIVAS": contagens.get("ATIVA", 0),
            "EM_ANALISE": contagens.get("EM_ANALISE", 0),
            "GANHAS": contagens.get("GANHA", 0),
            "PERDIDAS": contagens.get("PERDIDA", 0),
            "DESCARTADAS": contagens.get("DESCARTADA", 0),
            "TODOS": sum(contagens.values())
        },
        "processos": processos
    }
