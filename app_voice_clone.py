import os
import re
import tempfile
import datetime
import traceback
import torch
import gradio as gr
import soundfile as sf
import torchaudio
from TTS.api import TTS

# ==========================================
# PARCHES Y CONFIGURACIONES CRITICAS
# ==========================================

# 1. Parche para weights_only en PyTorch 2.6+
_original_load = torch.load
def _patched_load(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load

# 2. Parche para evitar crashes con TorchCodec dlls en Windows
def _safeload(filepath, *args, **kwargs):
    data, sr = sf.read(filepath, dtype='float32')
    if len(data.shape) == 1:
        data = data.reshape(-1, 1)
    return torch.from_numpy(data.T), sr
torchaudio.load = _safeload

os.environ["COQUI_TOS_AGREED"] = "1"

# ==========================================
# FASE 3: VALIDACION GPU MANDATORIA
# ==========================================
if not torch.cuda.is_available():
    raise RuntimeError(
        "No se ha detectado una GPU CUDA utilizable. "
        "Por politica del proyecto NO se permite ejecucion en CPU."
    )

device = "cuda"
print("Usando dispositivo:", device, "-", torch.cuda.get_device_name(0))
print("PyTorch:", torch.__version__, "CUDA:", torch.version.cuda)

print("Cargando modelo XTTSv2 de forma limpia...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print(f"Modelo XTTSv2 cargado correctamente en {device}")

# ==========================================
# FASE 2: PREPROCESAMIENTO DE TEXTO (REDUCIR SILENCIOS)
# ==========================================
def preprocess_text(text):
    # Unificar saltos de linea a espacios para que XTTS no los interprete como silencios largos
    text = re.sub(r'\n+', ' ', text)
    # Limitar puntuacion excesiva consecutiva que crea pausas molestas (ej: .... a ...)
    text = re.sub(r'\.{4,}', '...', text)
    # Reemplazar doble o triple espacio por uno solo
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ==========================================
# FASE 3: DIVISION DE CLIPS PARA GUIONES LARGOS
# ==========================================
def split_into_chunks(text, sentences_per_chunk=2):
    """
    Toma un texto grande, lo preprocesa para evitar silencios y luego
    lo separa en oraciones usando expresiones regulares simples y
    lo agrupa en chunks de 1 a 3 oraciones.
    """
    clean_text = preprocess_text(text)
    # Cortar por puntos o interrogaciones que tengan un espacio tras ellos (o fin de string)
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    
    chunks = []
    current_chunk = []
    for s in sentences:
        s = s.strip()
        if not s: continue
        current_chunk.append(s)
        if len(current_chunk) >= sentences_per_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    # Si por alguna razon no se corto nada, retornamos el minimo bloque sano
    return chunks if chunks else [clean_text]

# ==========================================
# LOGICA DE GENERACION (XTTSv2)
# ==========================================
def clone_single_voice(reference_audio, text, speed_val, temp_val):
    if reference_audio is None:
        raise ValueError("Debes subir una voz de referencia.")
    if not text or not text.strip():
        raise ValueError("Debes escribir un texto para locutar.")

    text_clean = preprocess_text(text)
    
    tmp_dir = tempfile.mkdtemp(prefix="xtts_")
    out_path = os.path.join(tmp_dir, "output.wav")

    # XTTSv2 acepta speed (afecta duracion del padding local interno)
    # Y temperature (mas bajo = robotico y predecible, mas alto = natural pero con riesgo a alucinacion)
    tts.tts_to_file(
        text=text_clean,
        speaker_wav=reference_audio,
        file_path=out_path,
        language="es",
        speed=speed_val,
        temperature=temp_val
    )

    return out_path, "✅ Audio generado exitosamente."

def clone_long_script(reference_audio, text, speed_val, temp_val):
    if reference_audio is None:
        raise ValueError("Debes subir una voz de referencia.")
    if not text or not text.strip():
        raise ValueError("Debes escribir un texto para locutar.")

    chunks = split_into_chunks(text, sentences_per_chunk=2)
    
    # Preparamos carpeta output
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(os.getcwd(), "outputs", timestamp)
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []
    
    for idx, chunk in enumerate(chunks, 1):
        filename = f"clip_{idx:03d}.wav"
        filepath = os.path.join(out_dir, filename)
        
        try:
            tts.tts_to_file(
                text=chunk,
                speaker_wav=reference_audio,
                file_path=filepath,
                language="es",
                speed=speed_val,
                temperature=temp_val
            )
            generated_files.append(filepath)
        except Exception as e:
            print(f"ERROR generando clip {idx}: {str(e)}")
            traceback.print_exc()
            
    return generated_files, f"✅ Generados {len(generated_files)} clips en la carpeta: outputs/{timestamp}"

# ==========================================
# WRAPPERS PARA GRADIO CON MANEJO DE ERRORES REALES
# ==========================================
def ui_wrapper_single(ref, txt, spd, tmp):
    try:
        return clone_single_voice(ref, txt, spd, tmp)
    except Exception as e:
        print("\n[!] ERROR CRITICO DURANTE LA GENERACION (MIRA EL TRACEBACK):")
        traceback.print_exc()
        raise gr.Error("Ocurrio un error al generar el audio. Revisa la terminal para mas detalles o vuelve a intentarlo con un fragmento de texto mas corto.")

def ui_wrapper_multi(ref, txt, spd, tmp):
    try:
        return clone_long_script(ref, txt, spd, tmp)
    except Exception as e:
        print("\n[!] ERROR CRITICO DURANTE LA GENERACION MULTIPLE:")
        traceback.print_exc()
        raise gr.Error("Ocurrio un error masivo generando los audios. Revisa la terminal.")

# ==========================================
# INTERFAZ GRAFICA (FASE 4)
# ==========================================
with gr.Blocks() as demo:
    gr.Markdown("# 🎙️ Clonador de Voz (XTTSv2) - Edicion Especial RTX 5070")
    
    gr.Markdown("""
    ### 📖 Cómo usar esta herramienta
    1. Graba un audio tuyo de 5–10 segundos, limpio, con tu micrófono.
    2. Súbelo como Voz de Referencia.
    3. Escribe el texto que quieras que tu clon diga.
    4. Ajusta Velocidad y Naturalidad si lo ves necesario.
    5. Haz clic en Generar voz clonada y descarga el WAV.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            ref_audio = gr.Audio(type="filepath", label="Voz de referencia (5–10 segundos, limpia)")
            
        with gr.Column(scale=1):
            gr.Markdown("### 🎛️ Afinación de Prosodia (XTTSv2)")
            speed_slider = gr.Slider(0.8, 1.3, value=0.95, label="Velocidad (speed)", info="Velocidad: mueve esto si habla demasiado rápido o demasiado lento.")
            temp_slider = gr.Slider(0.60, 0.90, value=0.75, step=0.01, label="Naturalidad (temperature)", info="Naturalidad: valores más altos suelen sonar menos robóticos, pero pueden introducir pequeñas variaciones erráticas.")
            
            def apply_curso_preset():
                return 0.90, 0.73  # Lento, didactico y controlado.
            
            btn_preset = gr.Button("🎓 Aplicar Preset: Modo curso en español", size="sm")
            btn_preset.click(fn=apply_curso_preset, outputs=[speed_slider, temp_slider])
            
    with gr.Tabs():
        # MODALIDAD 1: GOLPE RAPIDO
        with gr.Tab("⚡ Modo Rápido (Un Solo Clip)"):
            text_single = gr.Textbox(lines=6, label="Texto a locutar", placeholder="Escribe aquí el texto que dirá tu clon de voz...")
            gr.Markdown("*Consejo: escribe frases completas con puntuación normal. Evita muchos saltos de línea innecesarios para que la voz no meta silencios raros.*")
            
            btn_generate_single = gr.Button("Generar Voz Clonada", variant="primary")
            out_audio = gr.Audio(type="filepath", label="Voz clonada generada")
            out_status_single = gr.Textbox(label="Mensaje de Consola", interactive=False)
            
            btn_generate_single.click(
                fn=ui_wrapper_single,
                inputs=[ref_audio, text_single, speed_slider, temp_slider],
                outputs=[out_audio, out_status_single]
            )

        # MODALIDAD 2: DIVISION DE GUIONES (FASE 3)
        with gr.Tab("✂️ Dividir guion en varios clips"):
            gr.Markdown("*Utiliza este modo si quieres generar varias partes de un curso. Cada clip se guardará numerado para ayudarte a montarlos luego en tu editor de vídeo (DaVinci, Premiere, etc.).*")
            text_multi = gr.Textbox(lines=12, label="Pega tu Guion Completo aquí", placeholder="Ejemplo: Hola a todos. Hoy hablaremos de SQL. \nPrimero, las bases de datos relacionales...")
            
            btn_generate_multi = gr.Button("Dividir y Generar Todos los Clips", variant="primary")
            
            # Galeria o listado de archivos. gr.File() con `file_count="multiple"` soporta enviar listas de paths.
            out_files = gr.File(label="Archivos WAV Generados", file_count="multiple")
            out_status_multi = gr.Textbox(label="Mensaje de Consola", interactive=False)
            
            btn_generate_multi.click(
                fn=ui_wrapper_multi,
                inputs=[ref_audio, text_multi, speed_slider, temp_slider],
                outputs=[out_files, out_status_multi]
            )

    gr.Markdown("""
    ---
    **Documentación de Parámetros Reales de la API interna (`TTS.api.tts_to_file`)**
    - `speed` (Típicamente ~0.95 en español): El motor XTTS aplica Time-Stretch en el audio inferido sin perder demasiada calidad tímbrica.
    - `temperature` (Típicamente ~0.75): Controla la entropía de las predicciones del modelo. Un valor más bajo genera voces monótonas tipo "locutor AI", pero seguras (sin inventar sonidos). Valores entre 0.70 y 0.85 producen variaciones microscópicas de entonación y emoción (prosodia real humana), pero si se subir demasiado (>0.85) aumenta el riesgo de que el "Voice Clone" tartamudee o varíe la velocidad del habla abruptamente.
    """)

if __name__ == "__main__":
    print("Levantando Servidor Gradio local en el puerto 7861...")
    demo.queue().launch(server_name="127.0.0.1", server_port=7861, share=False)
