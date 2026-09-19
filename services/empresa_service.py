import sqlite3
import json
from datetime import datetime
from typing import Dict, Any
from services.pncp_client import get_conn

def inicializar_tabela_empresa():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_empresa (
            id INTEGER PRIMARY KEY DEFAULT 1,
            razao_social TEXT DEFAULT '',
            nome_fantasia TEXT DEFAULT '',
            cnpj TEXT DEFAULT '',
            inscricao_estadual TEXT DEFAULT '',
            inscricao_municipal TEXT DEFAULT '',
            porte TEXT DEFAULT 'EPP',
            endereco TEXT DEFAULT '',
            cidade_uf TEXT DEFAULT '',
            telefone TEXT DEFAULT '',
            email_contato TEXT DEFAULT '',
            representante_nome TEXT DEFAULT '',
            representante_cpf TEXT DEFAULT '',
            representante_cargo TEXT DEFAULT 'Sócio-Administrador',
            banco_nome TEXT DEFAULT '',
            banco_agencia TEXT DEFAULT '',
            banco_conta TEXT DEFAULT '',
            chave_pix TEXT DEFAULT '',
            val_cnd_federal TEXT DEFAULT '',
            val_crf_fgts TEXT DEFAULT '',
            val_cndt_trabalhista TEXT DEFAULT '',
            val_cnd_estadual TEXT DEFAULT '',
            val_cnd_municipal TEXT DEFAULT '',
            ramo_atuacao TEXT DEFAULT '',
            cnae_principal TEXT DEFAULT '',
            outros_documentos_json TEXT DEFAULT '[]',
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM dados_empresa WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO dados_empresa (id, razao_social, nome_fantasia, porte) VALUES (1, 'MINHA DISTRIBUIDORA E COMÉRCIO LTDA', 'RADAR PHARMA', 'EPP')")
    
    cursor.execute("PRAGMA table_info(dados_empresa)")
    colunas_db = [c[1] for c in cursor.fetchall()]
    if "outros_documentos_json" not in colunas_db:
        cursor.execute("ALTER TABLE dados_empresa ADD COLUMN outros_documentos_json TEXT DEFAULT '[]'")
    
    cursor.execute("PRAGMA table_info(dados_empresa)")
    colunas_db = [c[1] for c in cursor.fetchall()]
    if "ramo_atuacao" not in colunas_db:
        cursor.execute("ALTER TABLE dados_empresa ADD COLUMN ramo_atuacao TEXT DEFAULT ''")
    if "cnae_principal" not in colunas_db:
        cursor.execute("ALTER TABLE dados_empresa ADD COLUMN cnae_principal TEXT DEFAULT ''")
    conn.commit()
    conn.close()

def obter_dados_empresa() -> Dict[str, Any]:
    inicializar_tabela_empresa()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dados_empresa WHERE id = 1")
    linha = cursor.fetchone()
    colunas = [c[0] for c in cursor.description]
    conn.close()
    d = dict(zip(colunas, linha))
    try:
        d["outros_documentos"] = json.loads(d.get("outros_documentos_json") or "[]")
    except Exception:
        d["outros_documentos"] = []
    return d

def salvar_dados_empresa(dados: Dict[str, Any]) -> bool:
    inicializar_tabela_empresa()
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE dados_empresa SET
            razao_social = ?,
            nome_fantasia = ?,
            cnpj = ?,
            inscricao_estadual = ?,
            inscricao_municipal = ?,
            porte = ?,
            endereco = ?,
            cidade_uf = ?,
            telefone = ?,
            email_contato = ?,
            representante_nome = ?,
            representante_cpf = ?,
            representante_cargo = ?,
            banco_nome = ?,
            banco_agencia = ?,
            banco_conta = ?,
            chave_pix = ?,
            val_cnd_federal = ?,
            val_crf_fgts = ?,
            val_cndt_trabalhista = ?,
            val_cnd_estadual = ?,
            val_cnd_municipal = ?,
            ramo_atuacao = ?,
            cnae_principal = ?,
            outros_documentos_json = ?,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = 1
    ''', (
        dados.get("razao_social", "").strip(),
        dados.get("nome_fantasia", "").strip(),
        dados.get("cnpj", "").strip(),
        dados.get("inscricao_estadual", "").strip(),
        dados.get("inscricao_municipal", "").strip(),
        dados.get("porte", "EPP"),
        dados.get("endereco", "").strip(),
        dados.get("cidade_uf", "").strip(),
        dados.get("telefone", "").strip(),
        dados.get("email_contato", "").strip(),
        dados.get("representante_nome", "").strip(),
        dados.get("representante_cpf", "").strip(),
        dados.get("representante_cargo", "").strip(),
        dados.get("banco_nome", "").strip(),
        dados.get("banco_agencia", "").strip(),
        dados.get("banco_conta", "").strip(),
        dados.get("chave_pix", "").strip(),
        dados.get("val_cnd_federal", "").strip(),
        dados.get("val_crf_fgts", "").strip(),
        dados.get("val_cndt_trabalhista", "").strip(),
        dados.get("val_cnd_estadual", "").strip(),
        dados.get("val_cnd_municipal", "").strip(),
        dados.get("ramo_atuacao", "").strip(),
        dados.get("cnae_principal", "").strip(),
        json.dumps(dados.get("outros_documentos", []), ensure_ascii=False)
    ))
    conn.commit()
    conn.close()
    return True
