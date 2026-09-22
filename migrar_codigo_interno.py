import sqlite3
from datetime import datetime

conn = sqlite3.connect("database.db")
c = conn.cursor()

# 1. Verifica colunas existentes
c.execute("PRAGMA table_info(processos_licitatorios)")
cols = [col[1] for col in c.fetchall()]

novas_colunas = [
    ("empresa_id", "INTEGER DEFAULT 1"),
    ("ano", "INTEGER"),
    ("sequencial", "INTEGER"),
    ("codigo_interno", "TEXT")
]

for col_nome, col_tipo in novas_colunas:
    if col_nome not in cols:
        print(f"Adicionando coluna: {col_nome} ({col_tipo})")
        c.execute(f"ALTER TABLE processos_licitatorios ADD COLUMN {col_nome} {col_tipo}")

conn.commit()

# 2. Preencher retroativamente os processos existentes
c.execute("SELECT id, criado_em, empresa_id FROM processos_licitatorios ORDER BY id ASC")
processos = c.fetchall()

ano_contadores = {}

for proc_id, criado_em, emp_id in processos:
    emp = emp_id or 1
    # Extrai o ano da data de criação ou usa o ano corrente
    ano = datetime.now().year
    if criado_em and len(criado_em) >= 4:
        try:
            ano = int(criado_em[:4])
        except ValueError:
            pass
            
    chave = (emp, ano)
    ano_contadores[chave] = ano_contadores.get(chave, 0) + 1
    seq = ano_contadores[chave]
    cod = f"{seq:04d}/{ano}"

    c.execute("""
        UPDATE processos_licitatorios 
        SET empresa_id = ?, ano = ?, sequencial = ?, codigo_interno = ?
        WHERE id = ?
    """, (emp, ano, seq, cod, proc_id))

conn.commit()

# Verificação
c.execute("SELECT id, codigo_interno, numero_edital, orgao_nome FROM processos_licitatorios LIMIT 5")
print("\nAmostra de processos atualizados com código interno:")
for r in c.fetchall():
    print(r)

conn.close()
print("\nMigração concluída com sucesso!")
