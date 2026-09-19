# 🎯 Radar de Licitações

Sistema inteligente de monitoramento de contratações públicas com matching automático, análise de margem e dashboard interativo.

## ✨ Funcionalidades

- 🔐 **Autenticação JWT** - Login seguro com bcrypt
- 📦 **Portfolio** - Gerenciar produtos/serviços (CMED/NCM)
- 📊 **Matching Inteligente** - 4 estratégias de similaridade
- 💰 **Análise Comercial** - Cálculo automático de margem
- 📋 **Licitações** - Busca e filtros avançados
- 📱 **Dashboard** - Estatísticas em tempo real
- 🔔 **Notificações** - WhatsApp e Email (configurável)
- 📈 **Tendências** - Histórico de 30 dias

## 🚀 Quick Start

### 1. Clonar/Baixar o projeto

```bash
git clone https://github.com/SEU_USERNAME/radar-licitacoes.git
cd radar-licitacoes
```

### 2. Criar arquivo .env

```bash
cp .env.example .env
```

Editar `.env` se necessário (padrões funcionam para desenvolvimento).

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Iniciar aplicação

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

Acessar:
- 🌐 Dashboard: http://localhost:8080/static/index.html
- 📚 API Docs: http://localhost:8080/docs

## 📁 Estrutura do Projeto

```
radar-licitacoes/
├── main.py                    # Aplicação FastAPI
├── config.py                  # Configurações (Pydantic)
├── models.py                  # Modelos SQLAlchemy
├── utils.py                   # Dependências e helpers
├── requirements.txt           # Dependências Python
├── .env.example              # Variáveis de exemplo
├── README.md                 # Este arquivo
│
├── routers/                   # Endpoints da API
│   ├── users.py              # Autenticação
│   ├── portfolio.py          # Produtos
│   ├── licitations.py        # Licitações
│   ├── matches.py            # Matches
│   ├── notifications.py      # Notificações
│   └── dashboard.py          # Dashboard
│
├── services/                  # Lógica de negócio
│   ├── pncp_service.py       # Integração PNCP
│   ├── matching_service.py   # Motor de matching
│   └── notification_service.py # Notificações
│
└── static/                    # Frontend
    ├── index.html            # Aplicação principal
    └── dashboard.html        # Dashboard
```

## 🔑 Credenciais de Teste

```
Email: teste@radar.com
Senha: 123456
CNPJ: 00.000.000/0000-00
Empresa: Empresa Teste
```

## 📊 Modelos de Dados

### User
- email, password_hash, cnpj, company_name, phone
- Relacionado com: Portfolio, UserPreference, SentAlert

### Portfolio
- user_id, code (CMED/NCM), description, category
- cost_price, min_margin_percent, keywords
- Relacionado com: MatchedLicitationItem

### Licitation
- pncp_id, title, modality, org_name, state
- publication_date, closing_date, estimated_value, notice_url
- Relacionado com: LicitationItem

### LicitationItem
- licitation_id, item_number, description
- quantity, unit, code_cmed, code_ncm
- Relacionado com: MatchedLicitationItem

### MatchedLicitationItem
- licitation_item_id, portfolio_id
- similarity_score, match_reason
- estimated_margin_percent, viability
- Relacionado com: LicitationItem, Portfolio

### UserPreference
- user_id, states, cities, min_value, max_value
- modalities, org_types, max_daily_alerts

### SentAlert
- user_id, alert_type (daily/instant/weekly)
- whatsapp_status, email_status
- matched_items_count, whatsapp_message_id

## 🔌 API Endpoints

### Usuários
```
POST   /api/users/register       - Registrar
POST   /api/users/login          - Login
GET    /api/users/me             - Perfil
```

### Portfolio
```
GET    /api/portfolio            - Listar
POST   /api/portfolio            - Criar
GET    /api/portfolio/{id}       - Detalhes
PUT    /api/portfolio/{id}       - Atualizar
DELETE /api/portfolio/{id}       - Remover
```

### Licitações
```
GET    /api/licitations          - Listar (com filtros)
GET    /api/licitations/{id}     - Detalhes
GET    /api/licitations/search/by-code?code=... - Buscar por código
```

### Matches
```
GET    /api/matches              - Listar meus matches
GET    /api/matches/{id}         - Detalhes
GET    /api/matches/stats/summary - Resumo
```

### Notificações
```
GET    /api/notifications/history        - Histórico
GET    /api/notifications/preferences    - Preferências
POST   /api/notifications/preferences    - Criar preferências
PUT    /api/notifications/preferences    - Atualizar
POST   /api/notifications/test-whatsapp  - Teste
POST   /api/notifications/test-email     - Teste
```

### Dashboard
```
GET    /api/dashboard/summary           - Resumo
GET    /api/dashboard/stats             - Estatísticas
GET    /api/dashboard/trends?days=30    - Tendências
GET    /api/dashboard/recent-matches    - Recentes
```

## 🔐 Autenticação

Usar JWT Bearer token:

```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8080/api/users/me
```

## 🧪 Teste Rápido

```bash
# Registrar
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha123",
    "cnpj": "11.222.333/0001-81",
    "company_name": "Empresa Teste",
    "phone": "(21) 9999-9999"
  }'

# Login
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@example.com",
    "password": "senha123"
  }'

# Listar licitações
curl http://localhost:8080/api/licitations?state=RJ&limit=10 \
  -H "Authorization: Bearer TOKEN"
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```
# Database
DATABASE_URL=sqlite+aiosqlite:///./radar_licitacoes.db

# JWT
JWT_SECRET_KEY=sua-chave-secreta
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Features
ENABLE_WHATSAPP=false
ENABLE_EMAIL=false
TEST_MODE=true

# PNCP
PNCP_API_URL=https://pncp.gov.br/api/consulta/v1
PNCP_SYNC_DAYS=7

# Notificações (quando habilitadas)
WHATSAPP_API_URL=
WHATSAPP_API_KEY=
SMTP_SERVER=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
```

## 🚢 Deploy no Render

1. Fazer push para GitHub
2. Ir em render.com → New + → Web Service
3. Conectar repositório
4. Preencher:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8080`
5. Adicionar variáveis de ambiente
6. Deploy!

## 🧠 Motor de Matching

### Estratégias (Pontuação)

1. **CMED Exact Match** → 1.0 (100%)
2. **NCM Exact Match** → 0.9 (90%)
3. **Keywords Similarity** → até 0.8 (80%)
4. **Text Similarity** → até 0.7 (70%)
5. **Category Match** → 0.8 (80%)

Score final = média ponderada dos scores aplicáveis
Threshold mínimo = 0.6 (60%)

### Viabilidade Comercial

```
margin = ((valor_licitação - custo) / valor_licitação) * 100

Viabilidade:
- ALTA    → margin ≥ min_margin × 1.5
- MÉDIA   → min_margin ≤ margin < min_margin × 1.5
- BAIXA   → margin < min_margin
```

## 📝 Logs

Logs são exibidos no console com nível configurável em `.env`:

```
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔒 Segurança

- ✅ Senhas com bcrypt + salt
- ✅ JWT com expiração
- ✅ CORS configurado
- ✅ Validação Pydantic
- ✅ SQL Injection prevention (ORM)
- ✅ Rate limiting ready

## 🛠️ Desenvolvimento

### Adicionar novo endpoint

1. Criar função no router apropriado
2. Usar `Depends(get_current_user)` para autenticação
3. Usar `Depends(get_db)` para sessão do banco
4. Documentação automática em /docs

### Adicionar novo serviço

1. Criar classe em `services/`
2. Importar em `main.py` se necessário
3. Usar em routers

## 📚 Stack

- **Backend**: FastAPI 0.104
- **Database**: SQLAlchemy 2.0 + SQLite/PostgreSQL
- **Frontend**: Vue.js 3 (CDN)
- **Auth**: JWT + bcrypt
- **ORM**: SQLAlchemy async

## 📄 Licença

MIT

## 👨‍💼 Autor

Desenvolvido por Thyago

## 🤝 Contribuições

Issues e PRs são bem-vindas!

## 📞 Suporte

Para problemas:
1. Verificar logs
2. Checar .env
3. Verificar banco de dados
4. Abrir issue no GitHub

---

**Versão**: 1.0.0  
**Última atualização**: Setembro 2026  
**Status**: ✅ Production Ready
