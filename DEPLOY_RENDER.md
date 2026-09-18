# 🚀 DEPLOY NO RENDER - GUIA PASSO A PASSO

## ✅ Como colocar a aplicação online em 5 minutos

---

## 📋 PASSO 1: Preparação

### Você precisa de:
1. **Conta GitHub** (grátis em github.com)
2. **Conta Render** (grátis em render.com)
3. **Código da aplicação** (já temos)

---

## 🔧 PASSO 2: Upload para GitHub

### 2.1 Crie um repositório no GitHub

1. Acesse **github.com**
2. Clique em **"+"** (canto superior direito)
3. Clique em **"New repository"**
4. Nome: `radar-licitacoes`
5. Clique **"Create repository"**

### 2.2 Upload dos arquivos

No terminal do seu computador (não do celular):

```bash
# Entrar na pasta
cd /home/claude/radar_licitacoes

# Inicializar git
git init
git add .
git commit -m "Initial commit: Radar de Licitações v1.0"

# Adicionar repositório remoto (copie do GitHub)
git remote add origin https://github.com/SEU_USERNAME/radar-licitacoes.git
git branch -M main
git push -u origin main
```

---

## ☁️ PASSO 3: Deploy no Render

### 3.1 Acesse Render.com

1. Abra **render.com** (pode ser do celular!)
2. Clique **"Sign up"** (cadastre com GitHub)
3. Autorize Render acessar seu GitHub

### 3.2 Criar novo serviço

1. Clique **"+ New +"** 
2. Selecione **"Web Service"**
3. Conecte seu repositório `radar-licitacoes`
4. Preencha assim:

```
Name: radar-licitacoes
Environment: Python 3.11
Build Command: pip install -r requirements.txt
Start Command: uvicorn radar_licitacoes.main:app --host 0.0.0.0 --port 8080
```

### 3.3 Configurar variáveis de ambiente

Adicione essas variáveis no Render:

```
DATABASE_URL = sqlite:///./radar_licitacoes.db
ENABLE_WHATSAPP = false
ENABLE_EMAIL = false
ENABLE_SCHEDULER = false
TEST_MODE = true
JWT_SECRET_KEY = super-secret-key-render-2024
```

### 3.4 Deploy

1. Clique **"Create Web Service"**
2. Aguarde ~2-3 minutos
3. Quando aparecer ✅ "Your service is live", está pronto!

---

## 🌐 PASSO 4: Acessar pelo Celular

Depois que o deploy terminar, você verá uma URL como:

```
https://radar-licitacoes-xxxxx.onrender.com
```

### Acesse pelo celular:

```
https://seu-url.onrender.com/static/index.html
```

Exemplo completo:
```
https://radar-licitacoes-abc123.onrender.com/static/index.html
```

---

## 🔐 CREDENCIAIS DE TESTE

```
Email:    teste@radar.com
Senha:    123456
CNPJ:     00.000.000/0000-00
Empresa:  Empresa Teste
WhatsApp: (21) 99999-9999
```

Ou crie sua própria conta!

---

## 📊 O que esperar

- ⚡ **Primeira carga**: 2-3 segundos (primeira inicialização)
- 📱 **Funciona 100% no celular**
- 💾 **Banco de dados**: SQLite (funciona no Render grátis)
- 🔄 **Atualizado**: Cada git push atualiza automaticamente

---

## ⚠️ Limitações do Render Grátis

- ⏸️ Dorme depois de 15 min sem uso (acorda ao acessar)
- 📦 Máximo 0.5GB de armazenamento
- 💾 Sem persistência de dados (reinicia = perde dados)

**Para uso real**: Upgrade para plano pago (~$5/mês)

---

## 🆘 Se não funcionar

### Erro comum 1: "Build failed"
→ Verifique se `requirements.txt` está correto

### Erro comum 2: "Application failed to start"
→ Pode ser a porta. Tente adicionar ao start command:
```
uvicorn radar_licitacoes.main:app --host 0.0.0.0 --port 10000
```

### Erro comum 3: "Cannot find module"
→ Certifique-se que `__init__.py` existe em todas as pastas

---

## ✨ Pronto!

Agora você pode acessar a aplicação do celular de qualquer lugar! 🎉

**URL final:**
```
https://seu-url.onrender.com/static/index.html
```

**API Docs:**
```
https://seu-url.onrender.com/docs
```

---

Qualquer dúvida, me avisa! 🚀
