# Script para iniciar AgroVision AI no Windows PowerShell

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "AgroVision AI - Startup" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[...] Verificando Python..." -ForegroundColor Yellow
try {
    $python_version = python --version 2>$1
    Write-Host "[OK] Python encontrado: $python_version" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.11.15 de https://www.python.org" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host ""

# Criar .venv se não existir
if (-not (Test-Path ".venv")) {
    Write-Host "[INFO] Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

# Ativar .venv
Write-Host "[INFO] Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Instalar dependências
if (-not (Test-Path ".venv\Lib\site-packages\fastapi")) {
    Write-Host "[INFO] Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""

# Verificar Ollama
Write-Host "[...] Verificando Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags -ErrorAction Stop
    Write-Host "[OK] Ollama está disponível" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Ollama não está respondendo em http://127.0.0.1:11434" -ForegroundColor Yellow
    Write-Host "[INFO] Abra outro terminal PowerShell e execute: ollama serve" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione Enter para continuar"
}

Write-Host ""
Write-Host "[INFO] Iniciando AgroVision AI..." -ForegroundColor Cyan
Write-Host "[URL] http://127.0.0.1:8000" -ForegroundColor Green
Write-Host ""

python -m uvicorn app:app --reload
