#!/bin/bash

# 🚀 SCRIPT AUTOMÁTICO DE DEPLOY - RADAR DE LICITAÇÕES
# Execute este script no seu computador para fazer upload para GitHub

echo "================================"
echo "🚀 RADAR DE LICITAÇÕES - DEPLOY"
echo "================================"
echo ""

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não está instalado!"
    echo "Instale em: https://git-scm.com/download"
    exit 1
fi

# Pedir informações
echo "📋 Informações necessárias:"
echo ""
read -p "Seu username do GitHub: " GITHUB_USER
read -p "Token do GitHub (crie em https://github.com/settings/tokens): " GITHUB_TOKEN
read -p "Email do GitHub: " GITHUB_EMAIL

# Configurar git
echo ""
echo "⚙️  Configurando Git..."
git config --global user.email "$GITHUB_EMAIL"
git config --global user.name "$GITHUB_USER"

# Entrar na pasta do projeto
cd /home/claude/radar_licitacoes
echo "📂 Pasta: $(pwd)"

# Verificar se já é um repositório
if [ -d ".git" ]; then
    echo "✅ Já é um repositório git"
else
    echo "🆕 Criando novo repositório..."
    git init
fi

# Adicionar todos os arquivos
echo ""
echo "📝 Adicionando arquivos..."
git add .

# Fazer commit
echo "📦 Fazendo commit..."
git commit -m "🚀 Radar de Licitações v1.0 - Deploy inicial" || echo "⚠️  Já havia commit anterior"

# Renomear branch para main
git branch -M main

# Adicionar remote
REPO_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/radar-licitacoes.git"

if git remote | grep -q origin; then
    echo "🔄 Atualizando remote..."
    git remote remove origin
fi

echo "🔗 Conectando ao repositório..."
git remote add origin "$REPO_URL"

# Push
echo ""
echo "⬆️  Enviando para GitHub (isso pode demorar...)..."
git push -u origin main

echo ""
echo "✅ SUCESSO!"
echo ""
echo "Seu repositório está em:"
echo "https://github.com/${GITHUB_USER}/radar-licitacoes"
echo ""
echo "Próximo passo: Fazer deploy no Render"
echo "1. Acesse: https://render.com"
echo "2. Clique em 'New +' → 'Web Service'"
echo "3. Conecte seu repositório"
echo "4. Siga o guia DEPLOY_RENDER.md"
echo ""
