from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.empresa_service import obter_dados_empresa, salvar_dados_empresa
from services.pncp_client import get_conn

router = APIRouter(prefix="/api/empresa", tags=["Dados Cadastrais da Empresa"])

class EmpresaSchema(BaseModel):
    razao_social: Optional[str] = ""
    nome_fantasia: Optional[str] = ""
    cnpj: Optional[str] = ""
    inscricao_estadual: Optional[str] = ""
    inscricao_municipal: Optional[str] = ""
    porte: Optional[str] = "EPP"
    endereco: Optional[str] = ""
    cidade_uf: Optional[str] = ""
    telefone: Optional[str] = ""
    email_contato: Optional[str] = ""
    representante_nome: Optional[str] = ""
    representante_cpf: Optional[str] = ""
    representante_cargo: Optional[str] = "Sócio-Administrador"
    banco_nome: Optional[str] = ""
    banco_agencia: Optional[str] = ""
    banco_conta: Optional[str] = ""
    chave_pix: Optional[str] = ""
    val_cnd_federal: Optional[str] = ""
    val_crf_fgts: Optional[str] = ""
    val_cndt_trabalhista: Optional[str] = ""
    val_cnd_estadual: Optional[str] = ""
    val_cnd_municipal: Optional[str] = ""
    ramo_atuacao: Optional[str] = ""
    cnae_principal: Optional[str] = ""

class NovoUsuarioSchema(BaseModel):
    nome: str
    email: str
    funcao: Optional[str] = "OPERADOR" # ADMIN, OPERADOR, LEITOR

@router.get("")
async def get_empresa_endpoint():
    return {"sucesso": True, "empresa": obter_dados_empresa()}

@router.post("")
async def save_empresa_endpoint(dados: EmpresaSchema):
    ok = salvar_dados_empresa(dados.dict())
    return {"sucesso": ok, "mensagem": "Dados da empresa e certidões atualizados com sucesso!"}

# --- ENDPOINTS DE USUÁRIOS ---
def _garantir_tabela_usuarios():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_equipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            funcao TEXT DEFAULT 'OPERADOR',
            ativo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM usuarios_equipe")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios_equipe (nome, email, funcao, ativo) VALUES ('Administrador Principal', 'admin@empresa.com.br', 'ADMIN', 1)")
    conn.commit()
    conn.close()

@router.get("/usuarios")
async def listar_usuarios_equipe():
    _garantir_tabela_usuarios()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email, funcao, ativo, criado_em FROM usuarios_equipe ORDER BY id ASC")
    linhas = cursor.fetchall()
    conn.close()
    usuarios = [
        {"id": r[0], "nome": r[1], "email": r[2], "funcao": r[3], "ativo": bool(r[4]), "criado_em": r[5]}
        for r in linhas
    ]
    return {"sucesso": True, "usuarios": usuarios}

@router.post("/usuarios")
async def criar_usuario_equipe(dados: NovoUsuarioSchema):
    _garantir_tabela_usuarios()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios_equipe (nome, email, funcao) VALUES (?, ?, ?)", (dados.nome.strip(), dados.email.strip().lower(), dados.funcao))
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return {"sucesso": True, "mensagem": "Usuário adicionado à equipe com sucesso!", "id": novo_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Erro ao adicionar usuário: {str(e)}")

@router.delete("/usuarios/{usuario_id}")
async def remover_usuario_equipe(usuario_id: int):
    _garantir_tabela_usuarios()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios_equipe WHERE id = ?", (usuario_id,))
    conn.commit()
    conn.close()
    return {"sucesso": True, "mensagem": "Usuário removido da equipe."}
