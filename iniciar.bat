@echo off
chcp 65001 > nul
title Clonador Digital de Voz - XTTSv2
color 0A
cls

cd /d "%~dp0"

echo.
echo  ================================================================
echo    CLONADOR DIGITAL DE VOZ - XTTSv2  ^|  DonBorgiFR
echo    GPU: RTX 5070 Ti Blackwell  ^|  CUDA 12.8
echo  ================================================================
echo.
echo  [1/3] Activando entorno virtual Python...
call "%~dp0venv\Scripts\activate.bat"
if errorlevel 1 (
    echo  ERROR: No se pudo activar el entorno virtual.
    pause & exit /b 1
)

echo  [2/3] Configurando variables de entorno...
set COQUI_TOS_AGREED=1

echo  [3/3] Iniciando servidor Gradio en segundo plano...
echo.
echo  **********************************************************
echo  *  CARGANDO MODELO EN GPU... ESTO TARDA ~30-60 SEGUNDOS *
echo  *  El navegador se abrira SOLO cuando este 100%% listo   *
echo  **********************************************************
echo.

REM -- Lanzar Python en segundo plano y guardar PID --
start "GradioServer" /B python "%~dp0app_voice_clone.py" > "%~dp0server_log.txt" 2>&1

REM -- Esperar a que el puerto 7861 responda (loop cada 3 segundos, max 120s) --
echo  Esperando a que el modelo cargue...
set INTENTOS=0

:ESPERAR
set /a INTENTOS+=1
if %INTENTOS% GTR 40 (
    echo.
    echo  TIEMPO AGOTADO. Revisa server_log.txt para ver el error.
    pause
    exit /b 1
)

REM -- Comprobar si el puerto 7861 esta escuchando --
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:7861' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" > nul 2>&1
if %errorlevel% EQU 0 goto LISTO

REM -- Mostrar progreso --
set /a SEGUNDOS=%INTENTOS%*3
echo  ... %SEGUNDOS% segundos - aun cargando modelo en GPU...
timeout /t 3 /nobreak > nul
goto ESPERAR

:LISTO
echo.
echo  ================================================================
echo   SERVIDOR LISTO! Abriendo navegador en http://127.0.0.1:7861
echo  ================================================================
echo.
start "" "http://127.0.0.1:7861"

echo  La consola negra debe permanecer abierta mientras usas la app.
echo  Cierra esta ventana solo cuando hayas terminado de usarla.
echo.
pause
