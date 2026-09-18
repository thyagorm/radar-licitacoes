"""
Modelos de dados SQLAlchemy para o Radar de Licitações
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Usuário da plataforma"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    
    # Informações da empresa
    cnpj = Column(String, unique=True, nullable=False, index=True)
    company_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    
    # Status
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sent_alerts = relationship("SentAlert", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_users_email_active', 'email', 'active'),
    )


class Portfolio(Base):
    """Produtos/serviços que o usuário oferece"""
    __tablename__ = "portfolios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Código do produto
    code = Column(String, nullable=False)  # CMED ou NCM
    description = Column(String, nullable=False)
    category = Column(String, nullable=True)  # "medicamento", "produto", "serviço"
    
    # Preços
    cost_price = Column(Float, nullable=False)
    min_margin_percent = Column(Float, default=20.0)  # Margem mínima aceitável
    
    # Metadados
    keywords = Column(String, nullable=True)  # Palavras-chave separadas por vírgula
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="portfolios")
    matches = relationship("MatchedLicitationItem", back_populates="portfolio", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_portfolios_user_id_code', 'user_id', 'code'),
    )


class UserPreference(Base):
    """Preferências de busca do usuário"""
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Filtros geográficos
    states = Column(String, nullable=True)  # "RJ,SP,MG" separado por vírgula
    cities = Column(String, nullable=True)  # Cidades específicas
    
    # Filtros de valor
    min_value = Column(Float, nullable=True)  # Valor mínimo em R$
    max_value = Column(Float, nullable=True)  # Valor máximo em R$
    
    # Filtros de tipo
    modalities = Column(String, nullable=True)  # "pregão,concorrência,etc"
    org_types = Column(String, nullable=True)  # Tipos de órgão
    
    # Configuração de alertas
    max_daily_alerts = Column(Integer, default=10)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="preferences")


class Licitation(Base):
    """Licitações públicas"""
    __tablename__ = "licitations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pncp_id = Column(String, unique=True, nullable=False, index=True)  # ID do PNCP
    
    # Informações da licitação
    title = Column(String, nullable=False)
    modality = Column(String, nullable=True)  # pregão, concorrência, etc
    org_name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    
    # Datas
    publication_date = Column(DateTime, nullable=True, index=True)
    closing_date = Column(DateTime, nullable=True)
    
    # Valor
    estimated_value = Column(Float, nullable=True)
    
    # URL
    notice_url = Column(String, nullable=True)
    
    # Metadados
    extracted_keywords = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    items = relationship("LicitationItem", back_populates="licitation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_licitations_state_publication', 'state', 'publication_date'),
        Index('ix_licitations_estimated_value', 'estimated_value'),
    )


class LicitationItem(Base):
    """Itens específicos de cada licitação"""
    __tablename__ = "licitation_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    licitation_id = Column(String, ForeignKey("licitations.id"), nullable=False, index=True)
    
    item_number = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    
    # Especificações
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    
    # Códigos
    code_cmed = Column(String, nullable=True, index=True)  # CMED para medicamentos
    code_ncm = Column(String, nullable=True, index=True)   # NCM para produtos
    
    # Metadados
    extracted_keywords = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    licitation = relationship("Licitation", back_populates="items")
    matches = relationship("MatchedLicitationItem", back_populates="licitation_item", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_licitation_items_code_cmed', 'code_cmed'),
        Index('ix_licitation_items_code_ncm', 'code_ncm'),
    )


class MatchedLicitationItem(Base):
    """Matches encontrados entre portfolio e licitações"""
    __tablename__ = "matched_licitation_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    licitation_item_id = Column(String, ForeignKey("licitation_items.id"), nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    
    # Score e análise
    similarity_score = Column(Float, default=0.0)  # 0-100%
    match_reason = Column(String, nullable=True)  # "código CMED coincide", "keywords match", etc
    
    # Análise comercial
    estimated_margin_percent = Column(Float, nullable=True)
    viability = Column(String, default="média")  # "alta", "média", "baixa"
    
    # Datas
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    licitation_item = relationship("LicitationItem", back_populates="matches")
    portfolio = relationship("Portfolio", back_populates="matches")
    
    __table_args__ = (
        Index('ix_matched_items_score', 'similarity_score'),
        Index('ix_matched_items_viability', 'viability'),
    )


class SentAlert(Base):
    """Histórico de alertas enviados"""
    __tablename__ = "sent_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    alert_type = Column(String, default="daily")  # "daily", "instant", "weekly"
    
    # Status
    whatsapp_status = Column(String, nullable=True)  # "sent", "failed", "pending"
    email_status = Column(String, nullable=True)     # "sent", "failed", "pending"
    
    # Conteúdo
    matched_items_count = Column(Integer, default=0)
    whatsapp_message_id = Column(String, nullable=True)
    
    # Datas
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="sent_alerts")
    
    __table_args__ = (
        Index('ix_sent_alerts_user_created', 'user_id', 'created_at'),
    )


class CMEDPrice(Base):
    """Cache de preços CMED para referência"""
    __tablename__ = "cmed_prices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code_cmed = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=False)
    
    # Informações do medicamento
    principio_ativo = Column(String, nullable=True)
    concentracao = Column(String, nullable=True)
    forma_farmaceutica = Column(String, nullable=True)
    
    # Preços
    price_mg = Column(Float, nullable=True)
    price_unit = Column(Float, nullable=True)
    
    # Data de atualização
    last_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)