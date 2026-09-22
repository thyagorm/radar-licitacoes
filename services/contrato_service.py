import sqlite3
from typing import List, Dict, Any, Optional

DB_PATH = "database.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# 1. GESTÃO DOS ITENS DO PROCESSO
# ==========================================

def salvar_itens_processo(processo_id: int, itens: List[Dict[str, Any]]) -> bool:
    """
    Insere ou atualiza itens extraídos do edital/mapa no processo.
    """
    conn = get_conn()
    c = conn.cursor()
    
    # Remove itens anteriores caso seja reprocessado
    c.execute("DELETE FROM processo_itens WHERE processo_id = ?", (processo_id,))
    
    for item in itens:
        c.execute("""
            INSERT INTO processo_itens 
            (processo_id, numero_item, descricao, unidade, quantidade, valor_referencia_unitario, participar, preco_proposta_unitario, marca_fabricante)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            processo_id,
            item.get("numero_item", 1),
            item.get("descricao", ""),
            item.get("unidade", "UN"),
            float(item.get("quantidade", 0.0)),
            float(item.get("valor_referencia_unitario", 0.0)),
            item.get("participar", 1),
            float(item.get("preco_proposta_unitario", 0.0)),
            item.get("marca_fabricante", "")
        ))
    
    conn.commit()
    conn.close()
    return True

def listar_itens_processo(processo_id: int) -> List[Dict[str, Any]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM processo_itens WHERE processo_id = ? ORDER BY numero_item ASC", (processo_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ==========================================
# 2. HOMOLOGAÇÃO E CRIAÇÃO DO CONTRATO/ARP
# ==========================================

def homologar_vitoria_e_criar_contrato(
    processo_id: int,
    tipo_instrumento: str,
    numero_instrumento: str,
    data_inicio_vigencia: str,
    data_fim_vigencia: str,
    itens_ganhos: List[Dict[str, Any]], # [{"item_id": 1, "valor_homologado": 12.50}]
    observacoes: str = ""
) -> Dict[str, Any]:
    """
    Marca o processo como GANHA, homologa os itens vencedores e gera a ARP / Contrato.
    """
    conn = get_conn()
    c = conn.cursor()
    
    # 1. Atualiza status na tabela mãe
    c.execute("UPDATE processos_licitatorios SET status = 'GANHA', resultado = 'GANHOU' WHERE id = ?", (processo_id,))
    
    # 2. Atualiza os itens vencedores
    ids_ganhos = []
    valor_total_homologado = 0.0
    for g in itens_ganhos:
        item_id = g["item_id"]
        v_homologado = float(g.get("valor_homologado", 0.0))
        ids_ganhos.append(item_id)
        
        # Busca quantidade para somar o valor total homologado
        c.execute("SELECT quantidade FROM processo_itens WHERE id = ?", (item_id,))
        row = c.fetchone()
        qtd = row["quantidade"] if row else 0.0
        valor_total_homologado += (qtd * v_homologado)
        
        c.execute("""
            UPDATE processo_itens 
            SET vencedor = 1, valor_homologado_unitario = ?
            WHERE id = ?
        """, (v_homologado, item_id))
    
    # Desmarca os outros como não vencedores
    if ids_ganhos:
        placeholders = ",".join("?" for _ in ids_ganhos)
        c.execute(f"UPDATE processo_itens SET vencedor = 0 WHERE processo_id = ? AND id NOT IN ({placeholders})", [processo_id] + ids_ganhos)
    
    # 3. Cria o registro do Contrato / ARP
    c.execute("""
        INSERT INTO contratos 
        (processo_id, tipo_instrumento, numero_instrumento, data_inicio_vigencia, data_fim_vigencia, valor_total_homologado, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        processo_id,
        tipo_instrumento.upper(),
        numero_instrumento,
        data_inicio_vigencia,
        data_fim_vigencia,
        valor_total_homologado,
        observacoes
    ))
    contrato_id = c.lastrowid
    
    conn.commit()
    conn.close()
    return {"sucesso": True, "contrato_id": contrato_id, "valor_total": valor_total_homologado}

# ==========================================
# 3. GESTÃO DE ORDENS DE FORNECIMENTO (AF)
# ==========================================

def registrar_ordem_fornecimento(
    contrato_id: int,
    numero_af_empenho: str,
    prazo_limite_entrega: str,
    itens_af: List[Dict[str, Any]], # [{"processo_item_id": 1, "quantidade": 500}]
    data_emissao: str = "",
    observacoes: str = ""
) -> Dict[str, Any]:
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO ordens_fornecimento 
        (contrato_id, numero_af_empenho, data_emissao, prazo_limite_entrega, status, observacoes)
        VALUES (?, ?, ?, ?, 'PENDENTE', ?)
    """, (contrato_id, numero_af_empenho, data_emissao, prazo_limite_entrega, observacoes))
    ordem_id = c.lastrowid
    
    for it in itens_af:
        c.execute("""
            INSERT INTO ordem_fornecimento_itens (ordem_id, processo_item_id, quantidade_solicitada)
            VALUES (?, ?, ?)
        """, (ordem_id, it["processo_item_id"], float(it["quantidade"])))
        
    conn.commit()
    conn.close()
    return {"sucesso": True, "ordem_id": ordem_id}

def atualizar_entrega_af(ordem_id: int, data_entrega_efetiva: str) -> Dict[str, Any]:
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("SELECT prazo_limite_entrega FROM ordens_fornecimento WHERE id = ?", (ordem_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return {"sucesso": False, "mensagem": "AF não encontrada"}
        
    prazo = row["prazo_limite_entrega"]
    # Compara strings ISO YYYY-MM-DD
    status = "ENTREGUE_NO_PRAZO" if data_entrega_efetiva <= prazo else "ENTREGUE_COM_ATRASO"
    
    c.execute("""
        UPDATE ordens_fornecimento 
        SET data_entrega_efetiva = ?, status = ?
        WHERE id = ?
    """, (data_entrega_efetiva, status, ordem_id))
    
    conn.commit()
    conn.close()
    return {"sucesso": True, "status": status}

def obter_resumo_contrato(processo_id: int) -> Optional[Dict[str, Any]]:
    """
    Retorna o instrumento contratual, itens com saldo físico e financeiro restante, e histórico de AFs.
    """
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("SELECT * FROM contratos WHERE processo_id = ?", (processo_id,))
    row_contrato = c.fetchone()
    if not row_contrato:
        conn.close()
        return None
        
    contrato = dict(row_contrato)
    contrato_id = contrato["id"]
    
    # Busca itens vencedores com total entregue
    c.execute("""
        SELECT 
            pi.id,
            pi.numero_item,
            pi.descricao,
            pi.unidade,
            pi.quantidade AS quantidade_registrada,
            pi.valor_homologado_unitario,
            COALESCE(SUM(ofi.quantidade_solicitada), 0) AS quantidade_empenhada,
            (pi.quantidade - COALESCE(SUM(ofi.quantidade_solicitada), 0)) AS saldo_quantidade
        FROM processo_itens pi
        LEFT JOIN ordem_fornecimento_itens ofi ON pi.id = ofi.processo_item_id
        WHERE pi.processo_id = ? AND pi.vencedor = 1
        GROUP BY pi.id
        ORDER BY pi.numero_item ASC
    """, (processo_id,))
    itens = [dict(r) for r in c.fetchall()]
    
    # Busca ordens de fornecimento
    c.execute("""
        SELECT * FROM ordens_fornecimento 
        WHERE contrato_id = ? 
        ORDER BY id DESC
    """, (contrato_id,))
    ordens = [dict(r) for r in c.fetchall()]
    
    conn.close()
    return {
        "contrato": contrato,
        "itens": itens,
        "ordens_fornecimento": ordens
    }
