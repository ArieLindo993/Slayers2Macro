@echo off
echo Iniciando o atualizador Fishing Macro...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Atualizar.ps1"
pause
