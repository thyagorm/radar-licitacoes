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

@router.post("/executar-rotina-agendada")
async def forcar_execucao_rotina():
    from services.scheduler_service import tarefa_sincronizar_editais_pncp, tarefa_processar_digest_matinal
    await tarefa_sincronizar_editais_pncp()
    await tarefa_processar_digest_matinal()
    return {"sucesso": True, "mensagem": "Rotinas de sincronização e digest executadas com sucesso!"}

from services.notification_sender import enviar_email_digest, enviar_whatsapp_alerta

@router.post("/disparar-agora")
async def disparar_alertas_agora(dados: AlertasConfigSchema):
    # 1. Garante que os dados do formulário ficam salvos na base
    salvar_config_alertas(
        usuario_email=dados.usuario_email,
        whatsapp_telefone=dados.whatsapp_telefone or "",
        ufs=dados.ufs or "",
        palavras_chave=dados.palavras_chave or "",
        valor_minimo=dados.valor_minimo or 0.0,
        ativo=True
    )

    cfg = obter_config_alertas(dados.usuario_email) or {
        "usuario_email": dados.usuario_email,
        "whatsapp_telefone": dados.whatsapp_telefone,
        "ufs": dados.ufs,
        "palavras_chave": dados.palavras_chave,
        "valor_minimo": dados.valor_minimo
    }

    oportunidades = filtrar_oportunidades_para_usuario(cfg)
    msg_wpp = formatar_mensagem_whatsapp(oportunidades)
    email_html = formatar_email_html(oportunidades, dados.usuario_email)

    res_email = {"sucesso": False, "motivo": "SMTP_NAO_CONFIGURADO"}
    res_wpp = {"sucesso": False, "motivo": "WHATSAPP_NAO_CONFIGURADO"}

    if dados.usuario_email:
        res_email = enviar_email_digest(
            destinatario=dados.usuario_email,
            assunto="🎯 Oportunidades do Dia | Radar de Editais",
            conteudo_html=email_html
        )

    if dados.whatsapp_telefone:
        res_wpp = enviar_whatsapp_alerta(
            telefone=dados.whatsapp_telefone,
            mensagem_texto=msg_wpp
        )

    return {
        "sucesso": True,
        "total_oportunidades": len(oportunidades),
        "status_email": res_email,
        "status_whatsapp": res_wpp
    }

    msg_wpp = formatar_mensagem_whatsapp(oportunidades)
    email_html = formatar_email_html(oportunidades, usuario_email)

    res_email = {"sucesso": False, "motivo": "NAO_EXECUTADO"}
    res_wpp = {"sucesso": False, "motivo": "NAO_EXECUTADO"}

    # 1. Disparo de E-mail
    if usuario_email:
        res_email = enviar_email_digest(
            destinatario=usuario_email,
            assunto="🎯 Oportunidades do Dia | Radar de Editais",
            conteudo_html=email_html
        )

    # 2. Disparo de WhatsApp
    tel = cfg.get("whatsapp_telefone")
    if tel:
        res_wpp = enviar_whatsapp_alerta(telefone=tel, mensagem_texto=msg_wpp)

    return {
        "sucesso": True,
        "total_oportunidades": len(oportunidades),
        "status_email": res_email,
        "status_whatsapp": res_wpp,
        "mensagem": "Processo de envio finalizado. Verifique os status individuais."
    }
