@echo off
title 🎙️ Clonador digital de voz - XTTSv2 (GPU)
echo Iniciando Entorno Virtual...
call ".\venv\Scripts\activate"
echo Aceptando Terminos de Servicio de Coqui (COQUI_TOS_AGREED=1)...
set COQUI_TOS_AGREED=1
echo.
echo ==============================================
echo VERIFICANDO ARQUITECTURA (RTX Blackwell CUDA)
echo ==============================================
python "app_voice_clone.py"
pause
