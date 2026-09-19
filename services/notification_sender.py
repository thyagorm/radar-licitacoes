import os
import smtplib
import logging
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any

logger = logging.getLogger("notifications")

# Configurações de E-mail (SMTP)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Radar de Editais")

# Configurações de WhatsApp (Evolution API / Z-API)
# Exemplo Evolution: URL = https://sua-api.com/message/sendText/{instancia}
# Header: apikey
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "")

def enviar_email_digest(destinatario: str, assunto: str, conteudo_html: str) -> Dict[str, Any]:
    """
    Envia o e-mail formatado via SMTP nativo.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("Credenciais de SMTP não configuradas. Disparo de e-mail ignorado.")
        return {"sucesso": False, "motivo": "SMTP_NAO_CONFIGURADO"}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg["To"] = destinatario

        parte_html = MIMEText(conteudo_html, "html", "utf-8")
        msg.attach(parte_html)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [destinatario], msg.as_string())

        logger.info(f"E-mail enviado com sucesso para {destinatario}")
        return {"sucesso": True}
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {destinatario}: {e}")
        return {"sucesso": False, "erro": str(e)}

def enviar_whatsapp_alerta(telefone: str, mensagem_texto: str) -> Dict[str, Any]:
    """
    Dispara a mensagem via webhook HTTP para a API de WhatsApp (Evolution API / Z-API).
    """
    if not WHATSAPP_API_URL or not WHATSAPP_API_KEY:
        logger.warning("Configurações de WhatsApp API ausentes. Disparo de mensagem ignorado.")
        return {"sucesso": False, "motivo": "WHATSAPP_NAO_CONFIGURADO"}

    try:
        # Higieniza telefone (apenas números)
        num_limpo = "".join([c for c in telefone if c.isdigit()])
        if not num_limpo.startswith("55"):
            num_limpo = "55" + num_limpo

        headers = {
            "Content-Type": "application/json",
            "apikey": WHATSAPP_API_KEY
        }
        payload = {
            "number": num_limpo,
            "text": mensagem_texto
        }

        resp = requests.post(WHATSAPP_API_URL, json=payload, headers=headers, timeout=15)
        if resp.status_code in [200, 201]:
            logger.info(f"Alerta WhatsApp enviado com sucesso para {num_limpo}")
            return {"sucesso": True, "resposta": resp.json()}
        else:
            logger.error(f"Falha na API WhatsApp ({resp.status_code}): {resp.text}")
            return {"sucesso": False, "status_code": resp.status_code, "resposta": resp.text}
    except Exception as e:
        logger.error(f"Erro ao conectar com API WhatsApp: {e}")
        return {"sucesso": False, "erro": str(e)}
