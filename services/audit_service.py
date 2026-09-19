import sqlite3
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "database.db"

def init_audit_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_email TEXT DEFAULT 'anonimo@sistema.com',
            arquivo_nome TEXT,
            etapa TEXT,
            tipo_erro TEXT,
            detalhe_erro TEXT,
            stack_trace TEXT,
            payload_debug TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def registrar_log_erro(
    usuario_email: str = "usuario_padrao",
    arquivo_nome: str = "edital.pdf",
    etapa: str = "PROCESSAMENTO",
    tipo_erro: str = "ErroGeral",
    detalhe_erro: str = "",
    stack_trace: str = "",
    payload_debug: str = ""
):
    try:
        init_audit_db()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs_auditoria (
                usuario_email, arquivo_nome, etapa, tipo_erro, 
                detalhe_erro, stack_trace, payload_debug, data_hora
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            usuario_email,
            arquivo_nome,
            etapa,
            tipo_erro,
            detalhe_erro,
            stack_trace,
            payload_debug,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Falha ao gravar log de auditoria no banco: {e}")

def listar_logs_auditoria(limite: int = 50) -> List[Dict[str, Any]]:
    try:
        init_audit_db()
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, usuario_email, arquivo_nome, etapa, tipo_erro, 
                   detalhe_erro, stack_trace, payload_debug, data_hora
            FROM logs_auditoria
            ORDER BY id DESC
            LIMIT ?
        """, (limite,))
        linhas = cursor.fetchall()
        resultado = [dict(linha) for linha in linhas]
        conn.close()
        return resultado
    except Exception as e:
        print(f"Falha ao ler logs de auditoria: {e}")
        return []

def limpar_logs_auditoria():
    try:
        init_audit_db()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs_auditoria")
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False
