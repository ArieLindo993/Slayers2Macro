@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Atualizar.ps1" -Iniciar
if errorlevel 1 pause
