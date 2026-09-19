"""
Serviço de notificações WhatsApp e Email
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
from typing import List, Dict

logger = logging.getLogger(__name__)


class WhatsAppNotificationService:
    """Serviço para enviar notificações via WhatsApp"""
    
    def __init__(self):
        self.api_url = settings.whatsapp_api_url
        self.api_key = settings.whatsapp_api_key
        self.phone = settings.whatsapp_phone_number
    
    async def send_message(self, to_phone: str, message: str) -> bool:
        """
        Enviar mensagem WhatsApp
        
        Args:
            to_phone: Número de telefone de destino
            message: Mensagem a enviar
        
        Returns:
            True se enviado com sucesso
        """
        
        if not self.api_url or not self.api_key:
            logger.warning("WhatsApp não configurado")
            return False
        
        try:
            import aiohttp
            
            payload = {
                "phone": to_phone,
                "message": message
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status in (200, 201):
                        logger.info(f"✅ WhatsApp enviado para {to_phone}")
                        return True
                    else:
                        logger.error(f"❌ Erro ao enviar WhatsApp: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"❌ Erro ao enviar WhatsApp: {e}")
            return False


class EmailNotificationService:
    """Serviço para enviar notificações via Email"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from = settings.smtp_from
    
    async def send_message(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Enviar email
        
        Args:
            to_email: Email de destino
            subject: Assunto do email
            html_body: Corpo em HTML
        
        Returns:
            True se enviado com sucesso
        """
        
        if not self.smtp_server or not self.smtp_user:
            logger.warning("Email não configurado")
            return False
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_from or self.smtp_user
            msg["To"] = to_email
            
            # Adicionar corpo HTML
            part = MIMEText(html_body, "html")
            msg.attach(part)
            
            # Enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email enviado para {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {e}")
            return False


class NotificationOrchestrator:
    """Orquestrador de notificações"""
    
    def __init__(self):
        self.whatsapp = WhatsAppNotificationService()
        self.email = EmailNotificationService()
    
    async def send_daily_digest(
        self,
        user_email: str,
        user_phone: str,
        matches: List[Dict]
    ) -> Dict:
        """
        Enviar digest diário de matches
        
        Args:
            user_email: Email do usuário
            user_phone: Telefone do usuário
            matches: Lista de matches encontrados
        
        Returns:
            Status de envio
        """
        
        if not matches:
            return {
                "whatsapp_status": "skipped",
                "email_status": "skipped",
                "reason": "Nenhum match encontrado"
            }
        
        # Preparar conteúdo
        top_matches = matches[:5]  # Top 5 para WhatsApp
        
        whatsapp_msg = self._format_whatsapp_message(top_matches)
        email_body = self._format_email_body(matches)
        
        # Enviar WhatsApp (limitado)
        whatsapp_status = "skipped"
        if user_phone and len(top_matches) <= 5:
            success = await self.whatsapp.send_message(user_phone, whatsapp_msg)
            whatsapp_status = "sent" if success else "failed"
        
        # Enviar Email
        email_status = "skipped"
        if user_email:
            subject = f"Radar de Licitações - {len(matches)} novas oportunidades"
            success = await self.email.send_message(user_email, subject, email_body)
            email_status = "sent" if success else "failed"
        
        return {
            "whatsapp_status": whatsapp_status,
            "email_status": email_status,
            "matches_count": len(matches)
        }
    
    @staticmethod
    def _format_whatsapp_message(matches: List[Dict]) -> str:
        """Formata mensagem para WhatsApp"""
        
        lines = ["🎯 *Radar de Licitações - Alertas*", ""]
        
        for i, match in enumerate(matches, 1):
            lines.append(f"{i}. {match.get('product_name', 'Produto')}")
            lines.append(f"   📋 {match.get('licitation_title', 'Edital')}")
            lines.append(f"   📊 Score: {match.get('similarity_score', 0):.0f}%")
            lines.append(f"   💰 Margem: {match.get('estimated_margin_percent', 0):.1f}%")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_email_body(matches: List[Dict]) -> str:
        """Formata mensagem para Email em HTML"""
        
        html = """
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>🎯 Radar de Licitações</h2>
                <p>Olá! Encontramos <strong>{}</strong> novas oportunidades para seus produtos.</p>
                
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <tr style="background-color: #667eea; color: white;">
                        <th style="padding: 10px; text-align: left;">Produto</th>
                        <th style="padding: 10px; text-align: left;">Licitação</th>
                        <th style="padding: 10px; text-align: center;">Score</th>
                        <th style="padding: 10px; text-align: center;">Margem</th>
                        <th style="padding: 10px; text-align: center;">Viabilidade</th>
                    </tr>
        """.format(len(matches))
        
        for match in matches:
            viability_color = {
                "alta": "#28a745",
                "média": "#ffc107",
                "baixa": "#dc3545"
            }.get(match.get("viability", "média"), "#ffc107")
            
            html += f"""
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">{match.get('product_name', 'N/A')}</td>
                        <td style="padding: 10px;">{match.get('licitation_title', 'N/A')}</td>
                        <td style="padding: 10px; text-align: center;">{match.get('similarity_score', 0):.0f}%</td>
                        <td style="padding: 10px; text-align: center;">{match.get('estimated_margin_percent', 0):.1f}%</td>
                        <td style="padding: 10px; text-align: center; color: white; background-color: {viability_color};">
                            {match.get('viability', 'média').upper()}
                        </td>
                    </tr>
            """
        
        html += """
                </table>
                
                <p style="margin-top: 20px;">
                    Acesse seu dashboard para mais detalhes:
                    <a href="https://seu-dominio.com/dashboard">Abrir Dashboard</a>
                </p>
                
                <p style="color: #999; font-size: 12px;">
                    Radar de Licitações - Sistema de Monitoramento de Contratações Públicas
                </p>
            </body>
        </html>
        """
        
        return html


# Instância global
notification_service = NotificationOrchestrator()
