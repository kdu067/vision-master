@echo off
REM Script para iniciar AgroVision AI no Windows

echo.
echo ====================================
echo AgroVision AI - Startup
echo ====================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado. Instale Python 3.11.15
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Verificar se .venv existe
if not exist ".venv\" (
    echo [INFO] Criando ambiente virtual...
    python -m venv .venv
)

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call .\.venv\Scripts\Activate.ps1

REM Instalar dependências se requirements.txt foi atualizado
if not exist ".venv\Lib\site-packages\fastapi\" (
    echo [INFO] Instalando dependências...
    pip install -r requirements.txt
)

echo.
echo [INFO] Verificando Ollama...
powershell -Command "Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags" >nul 2>&1

if errorlevel 1 (
    echo [AVISO] Ollama não está respondendo em http://127.0.0.1:11434
    echo [INFO] Abra outro terminal e execute: ollama serve
    echo.
    pause
) else (
    echo [OK] Ollama está disponível
)

echo.
echo [INFO] Iniciando AgroVision AI...
echo [URL] http://127.0.0.1:8000
echo.

python -m uvicorn app:app --reload

pause
