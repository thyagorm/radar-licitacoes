# 🎯 Radar de Licitações

Sistema inteligente de monitoramento e análise de contratações públicas com alertas via WhatsApp e Email.

## 📋 Características

### ✅ Core Funcionalidades

1. **Sincronização com PNCP**
   - Leitura automática do Portal Nacional de Contratações Públicas
   - Atualização diária das licitações publicadas
   - Parsing inteligente de itens e valores

2. **Matching Inteligente**
   - Cruzamento automático entre itens de licitação e portfolio da empresa
   - Análise de similaridade por:
     - Código CMED/NCM (match perfeito)
     - Keywords e termos técnicos
     - Descrição e contexto
     - Categoria de produto/serviço

3. **Análise Comercial**
   - Cálculo automático de margem comercial
   - Viabilidade (alta/média/baixa) baseada em custos
   - Mapa de preços de referência

4. **Notificações Inteligentes**
   - **WhatsApp Business API**: Alertas rápidos e compactos (30 seg de leitura)
   - **Email**: Relatório completo do dia com análises detalhadas
   - Sem fidelidade: cancelamento self-service

5. **Dashboard Web**
   - Visualização de licitações em tempo real
   - Histórico de matches e oportunidades
   - Export em Excel com análises
   - Comparativo de margens ganhas vs perdidas

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    RADAR DE LICITAÇÕES v1.0                │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ PNCP API     │  │ Usuários     │  │ Portfolio    │
│ (Dados Abertos)│  │ (Email/Fone) │  │ (CMED/NCM)   │
└──────────────┘  └──────────────┘  └──────────────┘
       │                │                │
       └────────────────┴────────────────┘
              │
     ┌────────▼─────────┐
     │ FastAPI Backend  │
     │                  │
     ├─ Services:       │
     │  - PNCP Sync     │
     │  - Matching      │
     │  - Notifications │
     └────────┬─────────┘
              │
       ┌──────┴──────┐
       │             │
   ┌───▼───┐   ┌────▼────┐
   │  PostgreSQL │    Redis
   │  (Dados)    │    (Cache)
   └───────┘    └─────────┘

┌──────────────┬──────────────┬──────────────┐
│  WhatsApp    │    Email     │   Dashboard  │
│ Business API │     SMTP     │   Web (Vue)  │
└──────────────┴──────────────┴──────────────┘
```

## 📦 Stack Técnico

- **Backend**: FastAPI + SQLAlchemy + AsyncIO
- **Database**: PostgreSQL com AsyncPG
- **Scheduler**: APScheduler (jobs diários)
- **Notificações**: 
  - WhatsApp Business API (Meta)
  - SMTP (Gmail/Outlook)
- **Frontend**: Vue.js (opcional, recomendado)
- **Deploy**: Docker + Docker Compose

## 🚀 Instalação & Setup

### 1. Clonar e instalar dependências

```bash
git clone <repo>
cd radar_licitacoes
python -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` no Windows
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

Variáveis críticas:
- `DATABASE_URL`: PostgreSQL connection string
- `WHATSAPP_*`: Credenciais da API WhatsApp Business
- `SMTP_*`: Credenciais de email
- `JWT_SECRET_KEY`: Chave para autenticação

### 3. Inicializar banco de dados

```bash
python -c "from radar_licitacoes.models import Base; \
from sqlalchemy.orm import Session; \
from radar_licitacoes.config import settings; \
# Migrations (usar Alembic em produção)
```

### 4. Executar aplicação

```bash
# Desenvolvimento
uvicorn radar_licitacoes.main:app --reload

# Produção
gunicorn -w 4 -k uvicorn.workers.UvicornWorker radar_licitacoes.main:app
```

API estará disponível em: `http://localhost:8000`

## 📊 Fluxo de Funcionamento

### Diariamente

**06:00 AM - Sincronização (PNCP Sync Job)**
```
1. Buscar licitações publicadas (últimos 7 dias)
2. Extrair itens e metadados
3. Detectar códigos CMED/NCM
4. Salvar no PostgreSQL
5. Iniciar matching para todos os usuários
```

**07:00 AM - Envio de Digests (Send Digests Job)**
```
1. Buscar matches da última 24h por usuário
2. Agrupar por relevância (score)
3. Validar filtros de preferência (estado, valor, etc)
4. Calcular margens comerciais
5. Enviar via WhatsApp (compacto)
6. Enviar via Email (detalhado)
7. Registrar logs no banco
```

## 📡 API Endpoints

### Autenticação
```
POST   /api/users/register              - Criar conta
POST   /api/users/login                 - Login
GET    /api/users/me                    - Dados do usuário
```

### Portfolio
```
GET    /api/portfolio                   - Listar produtos/serviços
POST   /api/portfolio                   - Adicionar item
PUT    /api/portfolio/{id}              - Atualizar
DELETE /api/portfolio/{id}              - Remover
```

### Licitações
```
GET    /api/licitations                 - Listar licitações
GET    /api/licitations/{id}            - Detalhes
GET    /api/licitations/search          - Buscar por filtros
```

### Matches
```
GET    /api/matches                     - Meus matches
GET    /api/matches/{id}                - Detalhes do match
POST   /api/matches/{id}/export         - Export Excel
```

### Notificações
```
GET    /api/notifications/history       - Histórico de enviados
PUT    /api/notifications/preferences   - Alterar preferências
POST   /api/notifications/test-whatsapp - Testar WhatsApp
```

### Dashboard
```
GET    /api/dashboard/summary           - Resumo do dia
GET    /api/dashboard/stats             - Estatísticas
GET    /api/dashboard/trends            - Tendências
```

## 💰 Modelo de Negócio

| Tier | Preço | Features |
|------|-------|----------|
| **Free** | R$ 0 | 1 produto, 5 licitações/mês |
| **Pro** | R$ 49/mês | Ilimitado, WhatsApp + Email |
| **Enterprise** | Custom | API customizada, suporte 24/7 |

Garantia: 7 dias ou devolve o dinheiro.

## 🔒 Segurança

- JWT para autenticação
- Senhas com bcrypt (salted hashing)
- CORS configurado
- Rate limiting (opcional)
- Logs de todas as ações sensíveis
- Conformidade com Lei Geral de Proteção de Dados (LGPD)

## 📈 Performance & Escalabilidade

- **Async/Await**: Processamento não-bloqueante
- **Connection Pooling**: Pool PostgreSQL (20 conexões)
- **Caching**: Redis (opcional) para cache de CMED/NCM
- **Indexação**: Índices estratégicos no banco
- **Batch Processing**: Jobs processam lotes eficientemente

## 🧪 Testing

```bash
# Rodar testes
pytest tests/

# Com cobertura
pytest --cov=radar_licitacoes tests/

# Teste específico
pytest tests/test_matching.py::test_calculate_similarity_score
```

## 📝 Logs

Logs em `/logs/app.log` com níveis:
- `DEBUG`: Informações detalhadas
- `INFO`: Eventos normais
- `WARNING`: Possíveis problemas
- `ERROR`: Erros
- `CRITICAL`: Falhas críticas

## 🐳 Docker Compose

```yaml
# docker-compose.yml (incluído)
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: radar_licitacoes
  
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@db:5432/radar_licitacoes
```

Deploy:
```bash
docker-compose up -d
```

## 📞 Suporte & Contribuição

- **Issues**: GitHub Issues
- **Email**: support@radar-licitacoes.com.br
- **Changelog**: Ver CHANGELOG.md

## 📄 Licença

MIT License - veja LICENSE.md

---

**Desenvolvido com ❤️ por Thyago**
