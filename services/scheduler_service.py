import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from services.pncp_client import consultar_editais_pncp, persistir_editais_pncp, get_conn
from services.alert_service import (
    obter_config_alertas,
    filtrar_oportunidades_para_usuario,
    formatar_mensagem_whatsapp,
    formatar_email_html
)

logger = logging.getLogger("scheduler")
scheduler = AsyncIOScheduler()

async def tarefa_sincronizar_editais_pncp():
    """
    Executa a recolha periódica no PNCP para manter a base local alimentada.
    """
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logger.info(f"[{agora}] A iniciar sincronização automática com o PNCP...")
    try:
        ufs_padrao = ["RJ", "SP", "MG", "BA", "PR"]
        editais = consultar_editais_pncp(termo_busca=None, ufs=ufs_padrao, dias_atras=1, limite_por_uf=30)
        total_salvos = persistir_editais_pncp(editais)
        logger.info(f"Sincronização concluída com sucesso: {total_salvos} novos editais persistidos.")
    except Exception as e:
        logger.error(f"Erro durante a sincronização agendada do PNCP: {e}")

async def tarefa_processar_digest_matinal():
    """
    Percorre os utilizadores ativos e gera os resumos diários personalizados.
    """
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logger.info(f"[{agora}] A processar o Digest Matinal para os utilizadores ativos...")
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT usuario_email FROM user_alerts_config WHERE ativo = 1")
        utilizadores = [row[0] for row in cursor.fetchall()]
        conn.close()

        for email in utilizadores:
            config = obter_config_alertas(email)
            if not config:
                continue

            oportunidades = filtrar_oportunidades_para_usuario(config)
            if oportunidades:
                msg_wpp = formatar_mensagem_whatsapp(oportunidades)
                email_html = formatar_email_html(oportunidades, email)
                logger.info(f"Digest gerado para {email}: {len(oportunidades)} oportunidade(s) encontrada(s).")
                # Ponto de ligação futuro com APIs de envio (Z-API, Twilio, SMTP)
            else:
                logger.info(f"Sem novas oportunidades para o perfil de {email}.")

    except Exception as e:
        logger.error(f"Erro ao processar o Digest Matinal: {e}")

def iniciar_agendador():
    """
    Regista os gatilhos de tempo e inicia o agendador assíncrono.
    """
    if not scheduler.running:
        # Sincronização periódica (ex: de 4 em 4 horas)
        scheduler.add_job(
            tarefa_sincronizar_editais_pncp,
            trigger=CronTrigger(hour="*/4", minute="0"),
            id="sincronizacao_pncp",
            replace_existing=True
        )

        # Envio do Digest Matinal diário às 07h00
        scheduler.add_job(
            tarefa_processar_digest_matinal,
            trigger=CronTrigger(hour="7", minute="0"),
            id="digest_matinal_diario",
            replace_existing=True
        )

        scheduler.start()
        logger.info("Agendador de tarefas em segundo plano iniciado com sucesso!")

def parar_agendador():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Agendador de tarefas encerrado.")
