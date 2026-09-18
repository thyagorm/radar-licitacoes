# 🚀 SCRIPT PARA WINDOWS - RADAR DE LICITAÇÕES
# Execute este script no PowerShell para fazer upload para GitHub

Write-Host "================================" -ForegroundColor Cyan
Write-Host "🚀 RADAR DE LICITAÇÕES - DEPLOY" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se git está instalado
try {
    git --version | Out-Null
} catch {
    Write-Host "❌ Git não está instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://git-scm.com/download" -ForegroundColor Yellow
    exit 1
}

# Pedir informações
Write-Host "📋 Informações necessárias:" -ForegroundColor Yellow
Write-Host ""
$GITHUB_USER = Read-Host "Seu username do GitHub"
$GITHUB_TOKEN = Read-Host "Token do GitHub (crie em https://github.com/settings/tokens)" -AsSecureString
$GITHUB_TOKEN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($GITHUB_TOKEN))
$GITHUB_EMAIL = Read-Host "Email do GitHub"

# Configurar git
Write-Host ""
Write-Host "⚙️  Configurando Git..." -ForegroundColor Cyan
git config --global user.email "$GITHUB_EMAIL"
git config --global user.name "$GITHUB_USER"

# Entrar na pasta do projeto
$PROJECT_PATH = "C:\Users\$env:USERNAME\radar_licitacoes"
if (-not (Test-Path $PROJECT_PATH)) {
    $PROJECT_PATH = Read-Host "Caminho da pasta radar_licitacoes"
}

cd $PROJECT_PATH
Write-Host "📂 Pasta: $(Get-Location)" -ForegroundColor Green

# Verificar se já é um repositório
if (Test-Path ".git") {
    Write-Host "✅ Já é um repositório git" -ForegroundColor Green
} else {
    Write-Host "🆕 Criando novo repositório..." -ForegroundColor Yellow
    git init
}

# Adicionar todos os arquivos
Write-Host ""
Write-Host "📝 Adicionando arquivos..." -ForegroundColor Cyan
git add .

# Fazer commit
Write-Host "📦 Fazendo commit..." -ForegroundColor Cyan
git commit -m "🚀 Radar de Licitações v1.0 - Deploy inicial" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Já havia commit anterior" -ForegroundColor Yellow
}

# Renomear branch para main
git branch -M main

# Adicionar remote
$REPO_URL = "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/radar-licitacoes.git"

$REMOTES = git remote
if ($REMOTES -contains "origin") {
    Write-Host "🔄 Atualizando remote..." -ForegroundColor Yellow
    git remote remove origin
}

Write-Host "🔗 Conectando ao repositório..." -ForegroundColor Cyan
git remote add origin "$REPO_URL"

# Push
Write-Host ""
Write-Host "⬆️  Enviando para GitHub (isso pode demorar...)..." -ForegroundColor Cyan
git push -u origin main

Write-Host ""
Write-Host "✅ SUCESSO!" -ForegroundColor Green
Write-Host ""
Write-Host "Seu repositório está em:" -ForegroundColor Green
Write-Host "https://github.com/${GITHUB_USER}/radar-licitacoes" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximo passo: Fazer deploy no Render" -ForegroundColor Yellow
Write-Host "1. Acesse: https://render.com" -ForegroundColor White
Write-Host "2. Clique em 'New +' → 'Web Service'" -ForegroundColor White
Write-Host "3. Conecte seu repositório" -ForegroundColor White
Write-Host "4. Siga o guia DEPLOY_RENDER.md" -ForegroundColor White
Write-Host ""

Read-Host "Pressione Enter para sair"
