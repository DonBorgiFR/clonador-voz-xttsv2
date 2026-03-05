# 🎙️ Clonador de Voz Digital - Arquitectura XTTSv2

**GPU Requerida y Validada**: NVIDIA RTX 5070 Ti (Blackwell) vía CUDA 12.8 + PyTorch 2.10.

Este proyecto ha pivotado de la arquitectura experimental F5-TTS / Qwen hacia **Coqui XTTSv2 Zero-Shot**, mucho más rápido, natural, con mejor soporte al español y completamente renderizado en GPU Local. No se permite la ejecución silenciosa en CPU por diseño (Fail Fast if CPU).

---

## 📂 Estructura Limpia del Proyecto

El entorno de trabajo (carpeta raíz: `Clonación digital voz`) contiene exclusivamente lo necesario para el funcionamiento nativo de XTTS:

- `app_voice_clone.py`: Aplicación principal. Interfaz Gradio en el **puerto 7861**. Centraliza el procesamiento del texto, los parches críticos de PyTorch y torchaudio, y las funciones de clonación (un solo clip vs script largo dividido).
- `outputs/`: (Se generará automáticamente). Aquí se guardarán tus archivos `.wav` numerados cuando uses la herramienta de división de guiones.
- `venv/`: Entorno virtual Python con dependencias instaladas (Torch, Gradio, TTS, transformers versión `4.40.1`, soundfile, etc).
- `ffmpeg-master-latest-win64-gpl-shared/`: Binarios portables de FFmpeg usados por la API de inferencia TTS interna para gestionar transformaciones de audio si ocurren.
- `old_f5_tts_scripts/`: Directorio de archivo "Legacy". Contiene todos los intentos previos con F5-TTS, transcripciones, audios separados con demucs o código experimental de modelos de lenguaje Qwen que ya no aplica al pipeline actual.

---

## 🚀 Cómo Iniciar el Clonador

Simplemente haz doble clic sobre el script `iniciar.bat` que he generado o ejecuta:

```powershell
.\venv\Scripts\activate
$env:COQUI_TOS_AGREED=1
python app_voice_clone.py
```

Luego abre en tu navegador web: http://127.0.0.1:7861

---

## 🛠 Entendiendo los Parámetros de Síntesis (XTTS)
La interfaz expone los botones **Velocidad** y **Naturalidad**, pero por debajo XTTS está modificando variables complejas del pipeline de decodificación y de Vocoder:

1. **Velocidad (`speed`)**: 
   - El valor recomendado por defecto es **0.95**. Un valor de `1.0` puede sonar ligeramente acelerado en Castellano, así que bajarlo un poco al `0.9` es perfecto para dar ese tono pausado de clase o capacitación.
2. **Naturalidad (`temperature`)**:
   - XTTS predice qué tono y fonema vocal usar basado en probabilidades probabilísticas (GPT). Un `temperature` (Naturalidad) bajo (ej. `0.65`) obliga al modelo a usar las probabilidades más altas, sonando plano/monótono pero muy confiable (no inventa letras).
   - Un `temperature` más alto (ej. `0.75 - 0.85`) permite variaciones estocásticas en la voz, lo cual suena inmensamente más humano. Sin embargo, por diseño propio del modelo fundacional, empujar esto artificialmente puede generar tartamudeo en ciertas palabras muy raras. Si ves que tropieza, reduce la Temperatura a `0.70`.
3. **Puntuación**:
   - Una puntuación precisa (comas, puntos). El sistema borra saltos de línea largos automáticamente. No agregues "enters" vacíos en un texto.
   - Puntos (`.`) generan buenas pausas, útiles si quieres dar ritmo a la lectura.

---

## ⚠️ Parches Críticos que garantizan Funcionamiento (Para el desarrollador)
Dado que XTTSv2 de Coqui ya no tiene actualizaciones constantes y tú cuentas con un OS Windows 11 y Hardware PyTorch 2.6+, este sistema incorpora 2 monkey-patches mágicos que evitan crashes silenciosos. Nunca los remuevas de `app_voice_clone.py`:
- `torch.load = _patched_load`: Permite a PyTorch no-explotar cargando archivos `.bin` con `weights_only=False` (nuevo requisito de seguridad Torch).
- `torchaudio.load = _safeload`: Fuerza a que en todo momento Windows procese los archivos WAV con `soundfile` saltándose la DLL averiada de TorchCodec nativa.

¡Disfrútalo!
