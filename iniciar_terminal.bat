@echo off
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo ERRO: ambiente virtual nao encontrado.
    echo Execute a instalacao do Lancaster Access Terminal antes de iniciar.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" app.py

if errorlevel 1 (
    echo.
    echo O Lancaster Access Terminal foi encerrado com erro.
    pause
)