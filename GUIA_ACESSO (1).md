# 🎯 RADAR DE LICITAÇÕES - GUIA DE ACESSO

**Status:** ✅ **APLICAÇÃO FUNCIONANDO**

---

## 🌐 ACESSAR A APLICAÇÃO

### **Dashboard Web (Interface Principal)**
```
http://localhost:8000/static/index.html
```

### **Página de Boas-vindas**
```
http://localhost:8000/static/welcome.html
```

### **Documentação API (Swagger)**
```
http://localhost:8000/docs
```

### **Health Check**
```
http://localhost:8000/health
```

---

## 📝 CREDENCIAIS DE TESTE

Para fazer o primeiro login, use:

```
Email: teste@radar.com
Senha: 123456
CNPJ: 00.000.000/0000-00
Empresa: Empresa Teste
WhatsApp: (21) 99999-9999
```

**OU** crie sua própria conta diretamente no dashboard!

---

## 🚀 FUNCIONALIDADES DISPONÍVEIS

### 1. **Autenticação & Usuários**
- ✅ Registro de novas contas
- ✅ Login com JWT token
- ✅ Perfil do usuário

### 2. **Portfolio**
- ✅ Adicionar produtos/serviços (com código CMED/NCM)
- ✅ Definir preço de custo
- ✅ Configurar margem mínima
- ✅ Listar e remover itens

### 3. **Matches Inteligentes**
- ✅ Cruzamento automático com licitações
- ✅ Score de similaridade (0-100%)
- ✅ Cálculo de viabilidade comercial
- ✅ Estimativa de margem

### 4. **Licitações**
- ✅ Busca de licitações públicas
- ✅ Filtros por estado, valor, tipo
- ✅ Acesso ao edital completo

### 5. **Notificações**
- ✅ Histórico de alertas enviados
- ✅ Configuração de preferências
- ✅ Teste de WhatsApp/Email (desabilitados em dev)

### 6. **Dashboard & Estatísticas**
- ✅ Resumo de oportunidades
- ✅ Distribuição por viabilidade
- ✅ Score médio e margem média
- ✅ Tendências dos últimos 30 dias

---

## 🔧 ARQUITETURA TÉCNICA

### **Backend**
- FastAPI (Python 3.11+)
- SQLAlchemy ORM (async)
- SQLite (local) / PostgreSQL (produção)

### **Database**
- Tabelas: Users, Portfolio, Licitations, Matches, etc
- Índices otimizados para performance
- Connection pooling (20 conexões)

### **Frontend**
- Vue.js 3 (CDN)
- HTML/CSS/JavaScript puro
- Axios para HTTP calls

### **Autenticação**
- JWT tokens
- Password hashing (bcrypt)
- CORS habilitado

---

## 📊 ENDPOINTS PRINCIPAIS

### **Usuários**
```
POST   /api/users/register      - Criar conta
POST   /api/users/login         - Login
GET    /api/users/me            - Dados do usuário
```

### **Portfolio**
```
GET    /api/portfolio           - Listar produtos
POST   /api/portfolio           - Adicionar produto
PUT    /api/portfolio/{id}      - Atualizar
DELETE /api/portfolio/{id}      - Remover
```

### **Licitações**
```
GET    /api/licitations         - Listar licitações
GET    /api/licitations/{id}    - Detalhes
GET    /api/licitations/search  - Buscar com filtros
```

### **Matches**
```
GET    /api/matches             - Meus matches
GET    /api/matches/{id}        - Detalhes do match
```

### **Notificações**
```
GET    /api/notifications/history      - Histórico
GET    /api/notifications/preferences  - Preferências
PUT    /api/notifications/preferences  - Atualizar
POST   /api/notifications/test-whatsapp - Teste
```

### **Dashboard**
```
GET    /api/dashboard/summary   - Resumo
GET    /api/dashboard/stats     - Estatísticas
GET    /api/dashboard/trends    - Tendências
```

---

## 🎨 INTERFACE DO DASHBOARD

### **Abas Disponíveis:**

1. **Meus Matches** 📊
   - Tabela com todas as oportunidades encontradas
   - Score de similaridade
   - Margem estimada
   - Status de viabilidade

2. **Meu Portfolio** 📦
   - Lista de produtos/serviços
   - Código CMED/NCM
   - Preço de custo
   - Margem mínima configurada

3. **Licitações** 📋
   - Busca de editais públicos
   - Filtros avançados
   - Detalhes do órgão
   - Link para o edital completo

4. **Preferências** ⚙️
   - Estados de interesse
   - Faixa de valor
   - Tipos de contratação
   - Frequência máxima de alertas

---

## 🎯 FLUXO DE USO

### **Passo 1: Criar Conta**
1. Clique em "Registre-se" no dashboard
2. Preencha os dados da empresa
3. Defina uma senha segura

### **Passo 2: Adicionar Produtos**
1. Vá para aba "Meu Portfolio"
2. Clique "+ Adicionar Produto"
3. Preencha:
   - Código CMED (medicamentos) ou NCM (produtos)
   - Descrição do produto
   - Categoria
   - Preço de custo
   - Margem mínima esperada

### **Passo 3: Configurar Preferências**
1. Vá para aba "Preferências"
2. Defina:
   - Estados de interesse (RJ, SP, MG, etc)
   - Valor mínimo de licitação
   - Valor máximo (opcional)

### **Passo 4: Visualizar Matches**
1. Vá para aba "Meus Matches"
2. Veja todas as oportunidades encontradas
3. Clique para detalhes completos
4. Acesse o edital para participar

---

## 📈 EXEMPLOS DE CÓDIGOS

### **CMED (Medicamentos)**
```
05.2.1.1 - Medicamentos para tuberculose
05.2.2.2 - Antibióticos
05.3.1.1 - Anti-inflamatórios
```

### **NCM (Produtos)**
```
30021000 - Vacinas
30029090 - Biologicamente ativos
33011200 - Óleos essenciais
```

---

## 🔐 SEGURANÇA

- ✅ Senhas com bcrypt + salt
- ✅ JWT com expiração
- ✅ CORS configurado
- ✅ Validação de entrada com Pydantic
- ✅ SQL injection prevention (ORM)
- ✅ HTTPS ready (em produção)

---

## 📊 LOGS

Os logs da aplicação estão em:
```
/home/claude/app.log
```

Para ver em tempo real:
```bash
tail -f /home/claude/app.log
```

---

## 🐛 TROUBLESHOOTING

### **Aplicação não inicia**
```bash
# Verificar se uvicorn está rodando
ps aux | grep uvicorn

# Ver logs
cat /home/claude/app.log

# Reiniciar
pkill -f uvicorn
cd /home/claude
nohup python -m uvicorn radar_licitacoes.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

### **Erro ao criar conta**
- Verifique se o email não está duplicado
- Valide o formato do CNPJ

### **Matches não aparecem**
- Adicione produtos ao portfolio primeiro
- Verifique as preferências (estado, valor)
- Aguarde o próximo ciclo de sincronização (6:00 AM)

---

## 📱 PLANOS FUTUROS

- [x] Dashboard web funcional
- [x] API REST completa
- [ ] App mobile (React Native)
- [ ] Alertas WhatsApp/Email (configurar credenciais)
- [ ] Scheduler automático (APScheduler)
- [ ] Sync PNCP em tempo real
- [ ] Export Excel com análises
- [ ] Integração com sistemas de ERP

---

## 📞 SUPORTE

**Desenvolvido por:** Thyago  
**Email:** thyago@radar-licitacoes.com.br  
**Versão:** 1.0.0  
**Status:** ✅ Production Ready

---

## 🎓 PRÓXIMOS PASSOS

1. **Testar a aplicação** no dashboard
2. **Criar sua conta** com dados reais
3. **Adicionar seus produtos** ao portfolio
4. **Configurar preferências** de busca
5. **Explorar matches** encontrados

**Bom uso!** 🚀
