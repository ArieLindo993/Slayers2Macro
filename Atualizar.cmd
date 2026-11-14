@echo off
echo Iniciando o atualizador Fishing Macro...
set "SCRIPT=%~dp0Atualizar.ps1"
if not exist "%SCRIPT%" (
    echo.
    echo Nao foi possivel localizar Atualizar.ps1 junto deste arquivo.
    echo Baixe Atualizador.zip e use Extrair Tudo antes de abrir Atualizar.cmd.
    echo Se ja extraiu o ZIP, confira se o antivirus colocou Atualizar.ps1 em quarentena.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%"
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo.
    echo O atualizador terminou com erro. Confira as instrucoes acima e tente novamente.
    pause
)
exit /b %RESULT%
