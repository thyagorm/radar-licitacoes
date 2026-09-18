# 📝 GUIA MANUAL - UPLOAD PARA GITHUB

## Se os scripts não funcionarem, faça manualmente:

---

## 🔑 PASSO 1: Gerar Token no GitHub

1. Acesse: **github.com/settings/tokens**
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Nome: `radar-deploy`
4. Marque as opções:
   - ✅ `repo` (acesso completo)
   - ✅ `workflow` (se quiser CI/CD)
5. Clique **"Generate token"**
6. **COPIE O TOKEN** (só aparece uma vez!)

---

## 📂 PASSO 2: Preparar Pasta Local

Copie toda a pasta `radar_licitacoes` para seu computador em um local fácil, como:

**Windows:**
```
C:\Users\SEU_USUARIO\radar_licitacoes
```

**Mac/Linux:**
```
~/radar_licitacoes
```

---

## 🐙 PASSO 3: Criar Repositório no GitHub

1. Acesse: **github.com/new**
2. Nome do repositório: `radar-licitacoes`
3. Descrição: `Sistema inteligente de monitoramento de licitações públicas`
4. Deixe **público** (importante!)
5. Clique **"Create repository"**

---

## 💻 PASSO 4: Configurar Git Localmente

Abra o terminal/PowerShell e execute:

```bash
# Entrar na pasta
cd ~/radar_licitacoes
# ou no Windows:
cd C:\Users\SEU_USUARIO\radar_licitacoes

# Configurar git
git config --global user.email "seu-email@gmail.com"
git config --global user.name "Seu Nome"

# Inicializar repositório
git init

# Adicionar todos os arquivos
git add .

# Fazer commit
git commit -m "🚀 Radar de Licitações v1.0 - Deploy inicial"

# Renomear branch
git branch -M main

# Adicionar remote (copie do GitHub)
# Será algo como:
git remote add origin https://github.com/SEU_USERNAME/radar-licitacoes.git

# Fazer push
git push -u origin main
```

**Será pedido:**
- Username: seu username do GitHub
- Password: **COLE O TOKEN AQUI** (não a senha!)

---

## ✅ Pronto!

Seu repositório está online em:
```
https://github.com/SEU_USERNAME/radar-licitacoes
```

---

## 🚀 Próximo: Deploy no Render

Veja: **DEPLOY_RENDER.md**

---

## 🆘 Erros comuns

### "Permission denied"
→ Verifique se copiou o token correto

### "fatal: remote origin already exists"
→ Execute: `git remote remove origin`

### "Could not authenticate"
→ Certifique-se que está usando o TOKEN, não a senha!

---

Qualquer dúvida, me avisa! 🤔
