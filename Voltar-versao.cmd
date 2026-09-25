@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Atualizar.ps1" -Voltar
if errorlevel 1 pause
