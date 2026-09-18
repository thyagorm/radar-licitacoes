"""
Configurações da aplicação usando Pydantic Settings
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./radar_licitacoes.db"
    
    # JWT
    jwt_secret_key: str = "seu-secret-key-mude-em-producao"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 horas
    
    # Features
    enable_whatsapp: bool = False
    enable_email: bool = False
    enable_scheduler: bool = False
    test_mode: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # API
    api_title: str = "Radar de Licitações"
    api_version: str = "1.0.0"
    api_description: str = "Sistema inteligente de monitoramento de licitações públicas"
    
    # PNCP
    pncp_api_url: str = "https://pncp.gov.br/api/consulta/v1"
    pncp_sync_days: int = 7
    
    # Notificações
    whatsapp_api_url: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None
    
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Instância global de configurações
settings = Settings()