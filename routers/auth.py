from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import sqlite3

router = APIRouter(prefix="/api/auth", tags=["Autenticação e Perfis"])

class CadastroUsuarioDTO(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo_perfil: str  # 'EMPRESA' ou 'CONSULTOR'
    cnpj_empresa: Optional[str] = None
    razao_social: Optional[str] = None
    ramo_atividade: Optional[str] = None

@router.post("/cadastrar")
def cadastrar_usuario(dados: CadastroUsuarioDTO):
    if dados.tipo_perfil not in ["EMPRESA", "CONSULTOR"]:
        raise HTTPException(status_code=400, detail="Perfil inválido. Escolha EMPRESA ou CONSULTOR.")

    conn = sqlite3.connect("radar_licitacoes.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_perfil) VALUES (?, ?, ?, ?)",
            (dados.nome, dados.email, dados.senha, dados.tipo_perfil)
        )
        usuario_id = cursor.lastrowid

        if dados.tipo_perfil == "EMPRESA":
            if not dados.cnpj_empresa or not dados.razao_social:
                raise HTTPException(status_code=400, detail="CNPJ e Razão Social são obrigatórios para empresas.")
            cursor.execute(
                "INSERT INTO empresas_clientes (usuario_id, razao_social, cnpj, ramo_atividade) VALUES (?, ?, ?, ?)",
                (usuario_id, dados.razao_social, dados.cnpj_empresa, dados.ramo_atividade or "Geral")
            )

        conn.commit()
        return {"status": "ok", "usuario_id": usuario_id, "tipo_perfil": dados.tipo_perfil}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
    finally:
        conn.close()

@router.get("/minhas-empresas/{usuario_id}")
def listar_empresas_do_usuario(usuario_id: int):
    conn = sqlite3.connect("radar_licitacoes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, razao_social, cnpj, ramo_atividade FROM empresas_clientes WHERE usuario_id = ?", (usuario_id,))
    linhas = cursor.fetchall()
    conn.close()

    return [
        {"id": r[0], "razao_social": r[1], "cnpj": r[2], "ramo_atividade": r[3]}
        for r in linhas
    ]
