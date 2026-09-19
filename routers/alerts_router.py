from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.alert_service import (
    salvar_config_alertas,
    obter_config_alertas,
    filtrar_oportunidades_para_usuario,
    formatar_mensagem_whatsapp,
    formatar_email_html
)

router = APIRouter()

class AlertasConfigSchema(BaseModel):
    usuario_email: str
    whatsapp_telefone: Optional[str] = ""
    ufs: Optional[str] = ""
    palavras_chave: Optional[str] = ""
    valor_minimo: Optional[float] = 0.0
    ativo: Optional[bool] = True

@router.post("/configurar")
async def salvar_configuracao(dados: AlertasConfigSchema):
    salvar_config_alertas(
        usuario_email=dados.usuario_email,
        whatsapp_telefone=dados.whatsapp_telefone or "",
        ufs=dados.ufs or "",
        palavras_chave=dados.palavras_chave or "",
        valor_minimo=dados.valor_minimo or 0.0,
        ativo=dados.ativo if dados.ativo is not None else True
    )
    return {"sucesso": True, "mensagem": "Configurações de alerta salvas com sucesso!"}

@router.get("/configuracao")
async def obter_configuracao(usuario_email: str):
    cfg = obter_config_alertas(usuario_email)
    if not cfg:
        return {
            "config": {
                "usuario_email": usuario_email,
                "whatsapp_telefone": "",
                "ufs": "",
                "palavras_chave": "",
                "valor_minimo": 0.0,
                "ativo": 1
            }
        }
    return {"config": cfg}

@router.get("/simular-digest")
async def simular_digest(usuario_email: str):
    cfg = obter_config_alertas(usuario_email)
    if not cfg:
        cfg = {
            "usuario_email": usuario_email,
            "ufs": "",
            "palavras_chave": "",
            "valor_minimo": 0.0
        }

    oportunidades = filtrar_oportunidades_para_usuario(cfg)
    msg_wpp = formatar_mensagem_whatsapp(oportunidades)
    email_html = formatar_email_html(oportunidades, usuario_email)

    return {
        "total_encontradas": len(oportunidades),
        "whatsapp_preview": msg_wpp,
        "email_html_preview": email_html,
        "oportunidades": oportunidades[:5]
    }
