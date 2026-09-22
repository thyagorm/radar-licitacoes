import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

# 1. Tabela de itens do processo (suporta os 30 do edital e marca os 10 de disputa)
c.execute("""
CREATE TABLE IF NOT EXISTS processo_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processo_id INTEGER NOT NULL,
    numero_item INTEGER,
    descricao TEXT NOT NULL,
    unidade TEXT DEFAULT 'UN',
    quantidade REAL DEFAULT 0,
    valor_referencia_unitario REAL DEFAULT 0.0,
    participar INTEGER DEFAULT 1, -- 1=Sim (disputando), 0=Não
    preco_proposta_unitario REAL DEFAULT 0.0,
    marca_fabricante TEXT,
    vencedor INTEGER DEFAULT 0,    -- 1=Item ganho no certame, 0=Perdido/Não ganho
    valor_homologado_unitario REAL DEFAULT 0.0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (processo_id) REFERENCES processos_licitatorios(id) ON DELETE CASCADE
)
""")

# 2. Tabela de Instrumentos Contratuais (ARP ou Contrato Fixo)
c.execute("""
CREATE TABLE IF NOT EXISTS contratos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processo_id INTEGER NOT NULL,
    tipo_instrumento TEXT NOT NULL, -- 'ARP' ou 'CONTRATO'
    numero_instrumento TEXT NOT NULL,
    data_inicio_vigencia TEXT,
    data_fim_vigencia TEXT,
    valor_total_homologado REAL DEFAULT 0.0,
    observacoes TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (processo_id) REFERENCES processos_licitatorios(id) ON DELETE CASCADE
)
""")

# 3. Tabela de Ordens de Fornecimento / Notas de Empenho (AF)
c.execute("""
CREATE TABLE IF NOT EXISTS ordens_fornecimento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contrato_id INTEGER NOT NULL,
    numero_af_empenho TEXT NOT NULL,
    data_emissao TEXT,
    prazo_limite_entrega TEXT,
    data_entrega_efetiva TEXT,
    status TEXT DEFAULT 'PENDENTE', -- 'PENDENTE', 'ENTREGUE_NO_PRAZO', 'ENTREGUE_COM_ATRASO'
    observacoes TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contrato_id) REFERENCES contratos(id) ON DELETE CASCADE
)
""")

# 4. Tabela de Itens da Ordem de Fornecimento (Abate de Saldo Item a Item)
c.execute("""
CREATE TABLE IF NOT EXISTS ordem_fornecimento_itens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ordem_id INTEGER NOT NULL,
    processo_item_id INTEGER NOT NULL,
    quantidade_solicitada REAL NOT NULL,
    FOREIGN KEY (ordem_id) REFERENCES ordens_fornecimento(id) ON DELETE CASCADE,
    FOREIGN KEY (processo_item_id) REFERENCES processo_itens(id)
)
""")

conn.commit()

# Verificação
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [r[0] for r in c.fetchall()]
print("Tabelas no banco database.db:")
for t in ["processos_licitatorios", "processo_itens", "contratos", "ordens_fornecimento", "ordem_fornecimento_itens"]:
    print(f" -> {t}: {'OK' if t in tabelas else 'FALTOU'}")

conn.close()
