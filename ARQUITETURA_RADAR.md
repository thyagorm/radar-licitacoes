# 📐 Arquitetura Técnica - Radar de Licitações

## Visão Geral

O Radar de Licitações é um sistema full-stack que integra:
1. **Coleta de dados** (PNCP API)
2. **Processamento inteligente** (Matching Engine)
3. **Distribuição de alertas** (WhatsApp + Email)
4. **Dashboard web** (React/Vue)

## 🏗️ Stack Técnico

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+ (opcional)
- **Job Scheduler**: APScheduler

### Frontend
- **Framework**: Vue.js 3 (recomendado)
- **UI Framework**: Vuetify 3
- **Charts**: Chart.js
- **HTTP Client**: Axios

### DevOps
- **Containerização**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **CI/CD**: GitHub Actions (opcional)
- **Monitoring**: Prometheus + Grafana (opcional)

## 📊 Modelos de Dados

### Entity Relationship Diagram (ERD)

```
┌──────────────────────┐
│      Users           │
├──────────────────────┤
│ id (PK)              │
│ email (UNIQUE)       │
│ phone (UNIQUE)       │
│ cnpj (UNIQUE)        │
│ company_name         │
│ password_hash        │
│ active               │
│ created_at           │
└──────────┬───────────┘
           │ 1:N
           │
      ┌────┴────┐
      │          │
  ┌───▼──────────┴──────┐
  │                     │
┌─┴─────────────┐  ┌────▼──────────────┐
│  Portfolio    │  │ UserPreference     │
│ (CMED/NCM)    │  │  (Filtros)        │
└─┬─────────────┘  └───────────────────┘
  │ 1:N
  │ (matches)
  │
  ├─────────────────────────────┐
  │                             │
┌─▼──────────────────┐  ┌──────▼────────┐
│ MatchedItemItems   │  │  Licitation    │
│   (Cruzamento)     │  │   (Editais)    │
└────────────────────┘  └──┬────────┬───┘
                           │ 1:N    │ 1:N
                           │        │
                      ┌────▼────┐  │
                      │  Itens   │◄─┘
                      │ (Produtos)
                      └──────────┘

┌──────────────────────┐
│   SentAlert          │
│  (Log de Enviados)   │
└──────────────────────┘
```

## 🔄 Fluxos de Dados

### 1. Sincronização de Licitações (Daily 06:00 AM)

```
PNCP API
  ↓
[PNCPService.fetch_licitations()]
  ├─ HTTP GET /licitacoes
  ├─ Paginate (max 100/page)
  ├─ Parse JSON
  └─ Return: List[Dict]
  ↓
[PNCPService.fetch_licitation_details()]
  ├─ HTTP GET /licitacoes/{id}
  ├─ Extract items
  └─ Extract keywords via regex
  ↓
[PNCPService.save_licitation_to_db()]
  ├─ Create Licitation record
  ├─ Create LicitationItem records
  └─ Commit to PostgreSQL
  ↓
[MatchingService.process_new_licitation()]
  ├─ Iterate all active users
  ├─ Iterate all user portfolios
  ├─ Calculate similarity_score
  ├─ Create MatchedLicitationItem
  └─ Commit matches
```

### 2. Matching Engine

```
For each [User, Portfolio, LicitationItem]:

┌─────────────────────────────────────────┐
│ 1. Validate Preference Filters          │
│    - Check: state, city, value_range    │
│    - Check: org_types, modalities       │
│    If NOT passed → return NULL          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. Calculate Similarity Score           │
│    Strategy 1: CMED/NCM Exact Match     │
│       if match → return (1.0, "perfect")│
│                                         │
│    Strategy 2: Keywords Jaccard         │
│       intersection / union               │
│       return (0.0-1.0)                  │
│                                         │
│    Strategy 3: Text SequenceMatcher     │
│       difflib.ratio() > 0.3              │
│       return (0.0-1.0)                  │
│                                         │
│    Strategy 4: Category Exact           │
│       if match → add +0.8               │
│                                         │
│    Final: Average of all scores         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. Threshold Check                      │
│    if score < MIN_SIMILARITY (0.6)      │
│       → return NULL                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. Calculate Commercial Viability       │
│    margin = ((unit_price - cost) / unit)│
│                                         │
│    viability:                           │
│    - margin < min → "baixa"             │
│    - margin < min*1.5 → "média"         │
│    - margin >= min*1.5 → "alta"         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. Create MatchedLicitationItem         │
│    - Save to DB                         │
│    - Used later for notifications       │
└─────────────────────────────────────────┘
```

### 3. Envio de Digests (Daily 07:00 AM)

```
For each [User]:

Fetch Matches from last 24h
  ↓
┌─────────────────────────────────┐
│ Format Data for Channels        │
└─────────────────────────────────┘
  ├─ WhatsApp: Compact (≤5 items)
  └─ Email: Full (≤10 items)
  ↓
┌────────────────────────┐  ┌─────────────────┐
│ Send WhatsApp Alert    │  │ Send Email Digest│
│  - API call            │  │  - SMTP Send    │
│  - Store message_id    │  │  - Store msg_id │
│  - Log status          │  │  - Log status   │
└────────────────────────┘  └─────────────────┘
  ↓
┌──────────────────────────────────────────┐
│ Record SentAlert in DB                   │
│  - user_id                               │
│  - whatsapp_status, email_status         │
│  - message_ids for tracking              │
│  - matched_items_count                   │
└──────────────────────────────────────────┘
```

## 🔐 Camadas de Segurança

### 1. Autenticação
- JWT token com exp time
- Refresh tokens para session renewal
- Password hashing com bcrypt + salt

### 2. Autorização
- Role-based access control (RBAC)
  - `admin`: Acesso total
  - `pro_user`: Acesso full features
  - `free_user`: Acesso limitado
  
### 3. Rate Limiting
```python
# Exemplo (implementar com SlowAPI)
@limiter.limit("100/minute")
async def api_endpoint(request: Request):
    pass
```

### 4. Data Protection
- HTTPS only (em produção)
- LGPD compliance:
  - Direito ao esquecimento
  - Data portability
  - Consent management
- Encrypted sensitive fields (senha)

## 📊 Índices de Banco de Dados

```sql
-- Performance critical
CREATE INDEX idx_user_cnpj_active ON users(cnpj, active);
CREATE INDEX idx_portfolio_user_code ON portfolios(user_id, code);
CREATE INDEX idx_licitation_status_date ON licitations(status, publication_date);
CREATE INDEX idx_item_licitation ON licitation_items(licitation_id);
CREATE INDEX idx_item_code ON licitation_items(code_cmed, code_ncm);
CREATE INDEX idx_matched_user_score ON matched_items(portfolio_id, similarity_score);
CREATE INDEX idx_alert_user_date ON sent_alerts(user_id, sent_at);
```

## ⚡ Otimizações de Performance

### 1. Database
- Connection pooling (max 20)
- Lazy loading relations
- Batch inserts para matches
- Índices estratégicos

### 2. API
- Response caching (Redis)
- Pagination: 100 items/page
- Async/await em todo place

### 3. Scheduler
- Staggered execution (évita spike)
- Lock mechanism (single instance)
- Graceful degradation (skip se timeout)

### 4. Frontend
- Lazy load components
- Virtual scrolling para listas grandes
- Service workers para offline

## 🌐 Deployment

### Desenvolvimento

```bash
# 1. Local com docker-compose
docker-compose up -d

# 2. Migrations
docker-compose exec app alembic upgrade head

# 3. Seed data (opcional)
docker-compose exec app python scripts/seed_demo.py

# 4. Access
# API: http://localhost:8000
# PGAdmin: http://localhost:5050
```

### Produção

```bash
# Option 1: AWS ECS + RDS + ALB
# - Containerize com ECR
# - Deploy com Terraform
# - RDS managed PostgreSQL
# - ALB para load balancing

# Option 2: DigitalOcean App Platform
# - Git push → auto deploy
# - Managed database
# - Built-in HTTPS

# Option 3: Self-hosted Kubernetes
# - Helm charts
# - StatefulSet for DB
# - Horizontal pod autoscaling
```

## 📈 Monitoramento

### Métricas Importantes

```
API:
  - Request latency (p50, p95, p99)
  - Error rate
  - Throughput (RPS)
  - 4xx/5xx errors

Database:
  - Query latency
  - Connection pool usage
  - Slow queries (>1s)

Jobs:
  - sync_licitations duration
  - send_digests success rate
  - matches created per run

Business:
  - Users activos
  - Matches por dia
  - Email/WhatsApp delivery rate
  - Churn rate
```

### Alertas Recomendados

```
- Job sync_licitations > 5min → Alert
- Email delivery rate < 95% → Alert
- DB connection pool full → Alert
- 5xx error rate > 1% → Alert
```

## 🔄 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
on: [push]

jobs:
  test:
    - Run pytest
    - Code coverage > 80%
    
  lint:
    - Black formatting
    - Flake8 checks
    - Type checking (mypy)
  
  build:
    - Docker build
    - Push to registry
  
  deploy:
    - Update ECS task definition
    - Rolling deployment
    - Health check
```

## 🚨 Disaster Recovery

### Backup Strategy

```
Daily:
  - Database dump S3
  - Point-in-time recovery
  
Weekly:
  - Full backup to cold storage
  - Test restore
  
Monthly:
  - Backup audit
  - Update disaster recovery plan
```

### Failover

```
- Multi-AZ database
- Read replicas
- Automated failover
- DNS switching via Route53
```

## 📝 API Documentation

Full OpenAPI (Swagger) em `/docs`

Cada endpoint documenta:
- Request/response schemas
- Query parameters
- Authentication required
- Rate limits
- Example requests/responses

Exemplo:
```python
@app.get("/api/licitations")
async def get_licitations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    state: Optional[str] = None,
    session: AsyncSession = Depends(get_db)
):
    """
    Listar licitações com filtros opcionais
    
    - **skip**: Offset para paginação
    - **limit**: Máximo de resultados (≤500)
    - **state**: Filtrar por UF (ex: "RJ")
    
    Returns lista de licitações com matches
    """
```

---

**Documento atualizado**: Dezembro 2024
**Autor**: Thyago
**Status**: Production Ready
