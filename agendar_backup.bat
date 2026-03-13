@echo off
setlocal
cd /d "%~dp0"

echo =======================================================
echo     AGENDADOR DE BACKUP - MARICA CIDADAO
echo =======================================================
echo.
echo Este script configurara o Windows para realizar backups 
echo diarios do banco de dados (SQLite) as 01:00 da manha.
echo.

:: Pegando o caminho absoluto do python na máquina local
set PYTHON_EXE=python

:: Comando completo para rodar a rotina do Django
set SCRIPT_CMD="%PYTHON_EXE% %~dp0manage.py backup_db"

echo Registrando tarefa no Windows Task Scheduler...
schtasks /create /tn "MaricaBackupDiario" /tr "%SCRIPT_CMD%" /sc daily /st 01:00 /ru System /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCESSO] Backup automatico agendado para rodar todos os dias as 01:00 AM.
) else (
    echo.
    echo [ERRO] Nao foi possivel agendar a tarefa. Verifique se voc^e abriu este arquivo como Administrador.
)

echo.
pause
