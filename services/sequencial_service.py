import sqlite3
from datetime import datetime

def gerar_proximo_codigo_interno(empresa_id: int = 1, db_path: str = "database.db") -> tuple[int, int, str]:
    """
    Retorna (ano, sequencial, codigo_interno) no formato '0001/2026'.
    Reseta anualmente e calcula isolado por empresa.
    """
    ano_atual = datetime.now().year
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COALESCE(MAX(sequencial), 0) + 1 
        FROM processos_licitatorios 
        WHERE empresa_id = ? AND ano = ?
    """, (empresa_id, ano_atual))
    
    proximo_seq = cursor.fetchone()[0]
    conn.close()
    
    codigo_formatado = f"{proximo_seq:04d}/{ano_atual}"
    return ano_atual, proximo_seq, codigo_formatado
