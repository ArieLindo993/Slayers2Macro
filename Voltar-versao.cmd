@echo off
set "SCRIPT=%~dp0Atualizar.ps1"
if not exist "%SCRIPT%" (
    echo Nao foi possivel localizar Atualizar.ps1. Extraia o Atualizador.zip inteiro antes de usar este atalho.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%" -Voltar
if errorlevel 1 pause
