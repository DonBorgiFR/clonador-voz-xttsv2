<div align="center">
  <h1>🎙️ Digital Voice Cloner (XTTSv2) - RTX 5070 Edition</h1>
  <p><strong>Un sistema local de clonación de voz Zero-Shot optimizado estrictamente para GPUs NVIDIA Blackwell (PyTorch 2.6+).</strong></p>
</div>

---

## 🚀 Vision General
Este repositorio alberga un entorno altamente pulido y optimizado para la clonación de voz local empleando el motor **XTTSv2** de Coqui. El enfoque de este proyecto no es experimental; está diseñado para producción de contenido (como lectura de guiones largos, audio-cursos y tutoriales) garantizando un rendimiento brutal e inferencia Zero-Shot usando la potencia completa de hardware de vanguardia (RTX 5070 / CUDA 12.8).

**Características principales:**
*   ⚡ **GPU Strict Enforcement:** Políticas de ejecución sin concesiones. Si no se detecta computación CUDA de alta velocidad, la app declina el *fallback* a CPU y se detiene automáticamente para ahorrar ineficiencias de tiempo.
*   🦾 **Zero-Shot Puro:** Solo necesitas un corte de audio (*.wav*) de 5 a 10 segundos, 100% limpio y sin ruido de fondo, para que el modelo clone el timbre, la cadencia y la prosodia del emisor.
*   ✂️ **División Inteligente de Guiones (Modo Split):** Procesa y pica guiones masivos en clips lógicos (*clip_001.wav, clip_002.wav...*) que luego podrás arrastrar ordenadamente a tu editor de video (DaVinci, Premiere, CapCut).
*   🛡️ **Cero Crasheos (Windows & PyTorch Patches):** Se incluyen *Monkey Patches* nativos en el motor para sortear los nuevos bloqueos de seguridad `weights_only=True` de PyTorch $\ge$ 2.6 y los *crashes* crónicos de las DLLs de `TorchCodec` / `torchaudio` en Windows 11.
*   🎛️ **Prosodia Controlable:** Controles granulares de `Speed` (duración/time-stretch local) y `Temperature` (variación entrópica vs predictibilidad robótica de la IA).

---

## ⚙️ Requisitos del Sistema
Debido a su diseño especializado de alto rango, se requiere la siguiente arquitectura:
*   **SO:** Windows 11 (Probado y adaptado para evitar fugas de binarios `FFmpeg/TorchCodec`).
*   **Hardware:** Tarjeta Gráfica NVIDIA con soporte CUDA (Mínimo recomendado equivalente a RTX Serie 3000+, validado en **GeForce RTX 5070 Ti Blackwell**).
*   **Python:** Entorno `>= 3.10`.
*   **Driver:** Compatible con CUDA `12.8` o similar.

---

## 🛠 Instalación Local

### 1. Clona el Repositorio
```powershell
git clone https://github.com/DonBorgiFR/clonador-voz-xttsv2.git
cd clonador-voz-xttsv2
```

### 2. Prepara e Instala el Entorno (Virtual)
El repositorio aísla las librerías críticas exactas para no romper compatibilidad futura (Módulo crucial: `transformers==4.40.1` combinado con `TTS`).
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

*(Es altamente probable que necesites instalar PyTorch de forma nativa desde su canal principal referenciando a dependencias `cu128` o similar: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`)*

---

## 🎮 Cómo Usar la Herramienta

Con el entorno activo y los binarios compilados, levantar la aplicación gráfica (Gradio) es de un solo click si estás en Windows, corriendo el script:

```bash
iniciar.bat
```
Si vas manual desde consola:
```powershell
$env:COQUI_TOS_AGREED=1
python app_voice_clone.py
```
*(Se levantará de manera local y en el puerto designado exclusivo `http://127.0.0.1:7861`)*.

### 🎛 Modalidades de Uso (Desde la Interfaz Gráfica)

*   **Pestaña Rápida (1 Solo Clip):** Un entorno de prueba. Sube el micrófono de entrada, tipea y ajusta.
*   **Pestaña Producción (Guión Largo):** Para scripts reales. Pega tu contenido completo (ej: 3 cuartillas de Word). Internamente el software lo pre-procesará eliminando saltos de línea inútiles y lo particionará en oraciones fluidas mediante regex inteligente (evitando largas pausas en blancos que desorientan al modelo LLM). Creará una carpeta en `/outputs/{FECHA_HORA}/` y volcará decenas de clips de 10-20 segundos perfectos para montar en secuencia.

---

## 🧠 Arquitectura y Parámetros

El proyecto no oculta los engranajes detrás de "Botones mágicos". Toda la depuración e inferencia es transparente a consola con el uso exhaustivo de la librería de `traceback`. Las variables accesibles en UI son un volcado directo de los hiperparámetros que atacan los tensores de inferencia interna `tts_to_file`:

*   📉 **Temperature (0.65 - 0.85):** Una temperatura agresiva (>0.85) le da "alma" y entonación hiperrealista a tu clon pero aumenta el riesgo de tartamudeos porque permite alta entropía. Un modo bajo genera un locutor monótono y sin pausas raras. (Recomendado estándar: `0.75`; Recomendado formal: `0.73`).
*   ⏱️ **Speed (~0.95):** Dado que la IA acelera fonemas latinos, reducir levemente este parámetro produce la ilusión óptica-acústica de un narrador de cursos "Didáctico y pausado".

---

## 👨‍💻 Autor y Mantenimiento
Desarrollado y mantenido para automatización personal y creadores de contenido avanzados por **DonBorgiFR** (borjafr91@gmail.com).

*(Este código utiliza de base los fabulosos pesos pre-entrenados licenciados de Coqui-TTS).*
