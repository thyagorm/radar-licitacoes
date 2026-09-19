import sqlite3
import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "database.db"
STORAGE_DIR = "storage/editais"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_storage_db():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    conn = get_conn()
    cursor = conn.cursor()
    
    # 1. Tabela de Editais Analisados (Histórico completo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS editais_analisados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_email TEXT NOT NULL,
            nome_arquivo TEXT NOT NULL,
            caminho_storage TEXT NOT NULL,
            hash_arquivo TEXT UNIQUE,
            tamanho_bytes INTEGER,
            total_itens INTEGER DEFAULT 0,
            total_matches INTEGER DEFAULT 0,
            laboratorios_filtro TEXT,
            resultado_json TEXT,
            data_upload TEXT,
            data_expiracao TEXT
        )
    """)

    # 2. Tabela de Memória de Equivalência (Zero Tokens para itens conhecidos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash_descricao TEXT UNIQUE,
            descricao_original TEXT NOT NULL,
            descricao_normalizada TEXT NOT NULL,
            principio_ativo TEXT NOT NULL,
            unidade_padrao TEXT,
            vezes_utilizado INTEGER DEFAULT 1,
            data_criacao TEXT,
            ultima_utilizacao TEXT
        )
    """)
    conn.commit()
    conn.close()

def calcular_hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.strip().upper().encode("utf-8")).hexdigest()

def salvar_edital_no_disco(conteudo_pdf: bytes, usuario_email: str, nome_arquivo: str) -> str:
    user_folder = os.path.join(STORAGE_DIR, usuario_email.replace("@", "_at_").replace(".", "_"))
    os.makedirs(user_folder, exist_ok=True)
    hash_pdf = hashlib.sha256(conteudo_pdf).hexdigest()[:16]
    nome_seguro = f"{hash_pdf}_{nome_arquivo}"
    caminho_final = os.path.join(user_folder, nome_seguro)
    with open(caminho_final, "wb") as f:
        f.write(conteudo_pdf)
    return caminho_final

def persistir_edital_analisado(
    usuario_email: str,
    nome_arquivo: str,
    caminho_storage: str,
    conteudo_pdf: bytes,
    total_itens: int,
    total_matches: int,
    laboratorios: List[str],
    resultado_itens: List[Dict[str, Any]]
) -> int:
    init_storage_db()
    conn = get_conn()
    cursor = conn.cursor()
    hash_arq = hashlib.sha256(conteudo_pdf).hexdigest()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
        INSERT OR REPLACE INTO editais_analisados (
            usuario_email, nome_arquivo, caminho_storage, hash_arquivo,
            tamanho_bytes, total_itens, total_matches, laboratorios_filtro,
            resultado_json, data_upload, data_expiracao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
    """, (
        usuario_email,
        nome_arquivo,
        caminho_storage,
        hash_arq,
        len(conteudo_pdf),
        total_itens,
        total_matches,
        json.dumps(laboratorios, ensure_ascii=False),
        json.dumps(resultado_itens, ensure_ascii=False),
        data_hora
    ))
    edital_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return edital_id

def alimentar_memoria_equivalencia(itens_extraidos: List[Dict[str, Any]], normalizar_func):
    init_storage_db()
    conn = get_conn()
    cursor = conn.cursor()
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    for item in itens_extraidos:
        desc = item.get("descricao", "").strip()
        principio = item.get("principio_ativo", "").strip()
        unidade = item.get("unidade", "UN")

        if not desc or not principio:
            continue

        desc_norm = normalizar_func(desc)
        hash_desc = calcular_hash_texto(desc_norm)

        cursor.execute("""
            INSERT INTO memoria_itens (
                hash_descricao, descricao_original, descricao_normalizada,
                principio_ativo, unidade_padrao, vezes_utilizado, data_criacao, ultima_utilizacao
            ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(hash_descricao) DO UPDATE SET
                vezes_utilizado = vezes_utilizado + 1,
                ultima_utilizacao = excluded.ultima_utilizacao
        """, (hash_desc, desc, desc_norm, principio, unidade, data_hora, data_hora))

    conn.commit()
    conn.close()

def buscar_item_na_memoria(descricao: str, normalizar_func) -> Optional[Dict[str, Any]]:
    init_storage_db()
    desc_norm = normalizar_func(descricao)
    hash_desc = calcular_hash_texto(desc_norm)

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT principio_ativo, unidade_padrao 
        FROM memoria_itens 
        WHERE hash_descricao = ?
    """, (hash_desc,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "principio_ativo": row["principio_ativo"],
            "unidade": row["unidade_padrao"]
        }
    return None

def obter_estatisticas_dashboard(usuario_email: Optional[str] = None) -> Dict[str, Any]:
    init_storage_db()
    conn = get_conn()
    cursor = conn.cursor()

    if usuario_email:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_editais,
                COALESCE(SUM(total_itens), 0) as soma_itens,
                COALESCE(SUM(total_matches), 0) as soma_matches
            FROM editais_analisados
            WHERE usuario_email = ?
        """, (usuario_email,))
    else:
        cursor.execute("""
            SELECT 
                COUNT(*) as total_editais,
                COALESCE(SUM(total_itens), 0) as soma_itens,
                COALESCE(SUM(total_matches), 0) as soma_matches
            FROM editais_analisados
        """)
    stats = dict(cursor.fetchone())

    # Total de itens aprendidos na memória
    cursor.execute("SELECT COUNT(*) as termos_memoria FROM memoria_itens")
    stats["termos_memoria"] = cursor.fetchone()["termos_memoria"]

    conn.close()
    return stats

def listar_ultimos_editais(limite: int = 15) -> List[Dict[str, Any]]:
    init_storage_db()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, usuario_email, nome_arquivo, tamanho_bytes, total_itens,
               total_matches, data_upload
        FROM editais_analisados
        ORDER BY id DESC
        LIMIT ?
    """, (limite,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
