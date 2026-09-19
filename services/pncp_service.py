"""
Serviço de integração com PNCP
"""
import logging
import aiohttp
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)


class PNCPService:
    """Serviço para buscar dados do PNCP"""
    
    def __init__(self):
        self.base_url = settings.pncp_api_url
        self.headers = {
            "User-Agent": "Radar-Licitacoes/1.0"
        }
    
    async def fetch_licitations(self, days: int = None):
        """
        Buscar licitações do PNCP
        
        Args:
            days: Número de dias anteriores para buscar (default: PNCP_SYNC_DAYS)
        
        Returns:
            Lista de licitações
        """
        if days is None:
            days = settings.pncp_sync_days
        
        # Calcular datas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/contratacoes"
                params = {
                    "dataInicio": start_date.strftime("%Y-%m-%d"),
                    "dataFim": end_date.strftime("%Y-%m-%d")
                }
                
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ {len(data.get('data', []))} licitações buscadas do PNCP")
                        return data.get("data", [])
                    else:
                        logger.error(f"❌ Erro ao buscar PNCP: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"❌ Erro na requisição PNCP: {e}")
            return []
    
    async def fetch_licitation_details(self, licitation_id: str):
        """
        Buscar detalhes de uma licitação específica
        
        Args:
            licitation_id: ID da licitação no PNCP
        
        Returns:
            Detalhes da licitação
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/contratacoes/{licitation_id}"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"❌ Erro ao buscar detalhes: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"❌ Erro na requisição: {e}")
            return None
    
    async def search_by_code(self, code: str):
        """
        Buscar licitações por código CMED/NCM
        
        Args:
            code: Código CMED ou NCM
        
        Returns:
            Lista de licitações
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/contratacoes"
                params = {"filtro": code}
                
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    else:
                        return []
        
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []


# Instância global
pncp_service = PNCPService()
