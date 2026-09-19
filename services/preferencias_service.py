import sqlite3
import json
from typing import Dict, Any
from services.pncp_client import get_conn

def inicializar_tabela_preferencias():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferencias_empresa (
            id INTEGER PRIMARY KEY DEFAULT 1,
            margem_minima REAL DEFAULT 20.0,
            margem_alvo REAL DEFAULT 30.0,
            imposto_medio REAL DEFAULT 12.0,
            ufs_atuacao TEXT DEFAULT '["RJ", "SP", "MG"]',
            segmentos TEXT DEFAULT '["MEDICAMENTOS"]',
            valor_minimo REAL DEFAULT 5000.0,
            valor_maximo REAL DEFAULT 50000000.0,
            palavras_chave TEXT DEFAULT 'amoxicilina, dipirona, paracetamol, soro, seringa',
            blacklist_termos TEXT DEFAULT 'limpeza, vigilância, transporte escolar, locação de veículos, obras civis',
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Registo inicial garantido
    cursor.execute("SELECT COUNT(*) FROM preferencias_empresa WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO preferencias_empresa (id) VALUES (1)")
    conn.commit()
    conn.close()

def obter_preferencias() -> Dict[str, Any]:
    inicializar_tabela_preferencias()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM preferencias_empresa WHERE id = 1")
    linha = cursor.fetchone()
    colunas = [c[0] for c in cursor.description]
    conn.close()

    dados = dict(zip(colunas, linha))
    try:
        dados["ufs_atuacao"] = json.loads(dados.get("ufs_atuacao") or "[]")
    except:
        dados["ufs_atuacao"] = ["RJ", "SP", "MG"]
    try:
        dados["segmentos"] = json.loads(dados.get("segmentos") or "[]")
    except:
        dados["segmentos"] = ["MEDICAMENTOS"]

    return dados

def salvar_preferencias(dados: Dict[str, Any]) -> bool:
    inicializar_tabela_preferencias()
    conn = get_conn()
    cursor = conn.cursor()

    ufs_str = json.dumps(dados.get("ufs_atuacao") or ["RJ", "SP"])
    segmentos_str = json.dumps(dados.get("segmentos") or ["MEDICAMENTOS"])

    cursor.execute('''
        UPDATE preferencias_empresa SET
            margem_minima = ?,
            margem_alvo = ?,
            imposto_medio = ?,
            ufs_atuacao = ?,
            segmentos = ?,
            valor_minimo = ?,
            valor_maximo = ?,
            palavras_chave = ?,
            blacklist_termos = ?,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (
        float(dados.get("margem_minima") or 20.0),
        float(dados.get("margem_alvo") or 30.0),
        float(dados.get("imposto_medio") or 12.0),
        ufs_str,
        segmentos_str,
        float(dados.get("valor_minimo") or 0.0),
        float(dados.get("valor_maximo") or 999999999.0),
        dados.get("palavras_chave", "").strip(),
        dados.get("blacklist_termos", "").strip()
    ))
    conn.commit()
    conn.close()
    return True
