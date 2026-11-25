"""
transcribir.py - Transcribe un archivo de audio (.mp3, .wav, .m4a, ...) a un .txt

Usa Whisper (modelo de reconocimiento de voz de OpenAI) a traves de la
libreria faster-whisper. Corre 100% local en tu PC: no necesita internet
(salvo la primera vez, para descargar el modelo) ni cuentas ni claves.

Uso desde CMD / PowerShell:
    python transcribir.py audio.mp3
    python transcribir.py audio.mp3 -o salida.txt
    python transcribir.py audio.mp3 --modelo medium --idioma es
    python transcribir.py audio.mp3 --tiempos

Uso desde Thonny:
    Abrir este archivo y apretar F5 (Run). Se abre una ventana para
    elegir el .mp3 y el .txt se guarda al lado del audio.
"""

import argparse
import os
import sys
import time

MODELOS = ["tiny", "base", "small", "medium", "large-v3", "turbo"]


def formatear_tiempo(segundos):
    segundos = int(segundos)
    h, resto = divmod(segundos, 3600)
    m, s = divmod(resto, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def cargar_modelo(nombre, usar_gpu):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: falta la libreria 'faster-whisper'.")
        print("Instalala con:   pip install faster-whisper")
        print("(En Thonny: Herramientas > Administrar paquetes > buscar 'faster-whisper')")
        sys.exit(1)

    if usar_gpu:
        try:
            return WhisperModel(nombre, device="cuda", compute_type="float16")
        except Exception as e:  # sin CUDA / sin GPU NVIDIA
            print(f"Aviso: no se pudo usar la GPU ({e}). Sigo con CPU.")
    return WhisperModel(nombre, device="cpu", compute_type="int8")


def cargar_audio(ruta_audio, frecuencia=16000):
    """Decodifica el audio a mono 16 kHz (float32), como lo espera Whisper.

    Reemplaza a faster_whisper.decode_audio, que llama a av.open(...,
    metadata_errors=...) y se rompe con las versiones nuevas de PyAV
    (las unicas que tienen instalador listo para Python 3.15).
    """
    import io
    import av
    import numpy as np

    try:
        contenedor = av.open(ruta_audio, mode="r", metadata_errors="ignore")
    except TypeError:  # PyAV nuevo: ya no existe metadata_errors
        contenedor = av.open(ruta_audio, mode="r")

    resampler = av.audio.resampler.AudioResampler(
        format="s16", layout="mono", rate=frecuencia)
    buffer = io.BytesIO()
    with contenedor:
        frames = contenedor.decode(audio=0)
        while True:
            try:
                frame = next(frames)
            except StopIteration:
                break
            except av.error.InvalidDataError:  # frame danado: se saltea
                continue
            for f in resampler.resample(frame):
                buffer.write(f.to_ndarray().tobytes())
        for f in resampler.resample(None):  # vacia lo que quedo pendiente
            buffer.write(f.to_ndarray().tobytes())

    audio = np.frombuffer(buffer.getbuffer(), dtype=np.int16)
    return audio.astype(np.float32) / 32768.0


def transcribir(ruta_audio, ruta_salida=None, modelo="small", idioma="es",
                tiempos=False, usar_gpu=False):
    if idioma in (None, "", "auto"):
        idioma = None  # Whisper detecta el idioma solo
    if not os.path.isfile(ruta_audio):
        print(f"ERROR: no existe el archivo: {ruta_audio}")
        sys.exit(1)

    if ruta_salida is None:
        ruta_salida = os.path.splitext(ruta_audio)[0] + ".txt"

    print(f"Cargando modelo '{modelo}' (la primera vez se descarga, puede tardar)...")
    m = cargar_modelo(modelo, usar_gpu)

    # El filtro de silencios (VAD) necesita onnxruntime, que no existe para
    # todas las versiones de Python (ej. 3.15). Si no esta, se transcribe igual.
    try:
        import onnxruntime  # noqa: F401
        usar_vad = True
    except ImportError:
        usar_vad = False
        print("Aviso: 'onnxruntime' no esta instalado; transcribo sin filtro de silencios.")

    print(f"Transcribiendo: {ruta_audio}")
    inicio = time.time()
    audio = cargar_audio(ruta_audio)
    segmentos, info = m.transcribe(
        audio,
        language=idioma,      # "es" por defecto; None = detecta el idioma solo
        beam_size=5,
        vad_filter=usar_vad,  # saltea silencios
    )
    print(f"Idioma detectado: {info.language} "
          f"(probabilidad {info.language_probability:.0%}) - "
          f"duracion {formatear_tiempo(info.duration)}")

    lineas = []
    for seg in segmentos:
        texto = seg.text.strip()
        if not texto:
            continue
        if tiempos:
            linea = f"[{formatear_tiempo(seg.start)} - {formatear_tiempo(seg.end)}] {texto}"
        else:
            linea = texto
        lineas.append(linea)
        # progreso en pantalla
        print(f"  {formatear_tiempo(seg.end)} / {formatear_tiempo(info.duration)}  {texto}")

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"\nListo en {time.time() - inicio:.0f} s. Transcripcion guardada en:")
    print(f"  {os.path.abspath(ruta_salida)}")
    return ruta_salida


def elegir_archivo_con_ventana():
    """Para Thonny / doble click: abre un dialogo para elegir el audio."""
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        return input("Ruta del archivo .mp3: ").strip().strip('"')

    raiz = tk.Tk()
    raiz.withdraw()
    raiz.attributes("-topmost", True)
    ruta = filedialog.askopenfilename(
        title="Elegi el audio a transcribir",
        filetypes=[("Audio", "*.mp3 *.wav *.m4a *.ogg *.flac *.opus *.aac"),
                   ("Todos", "*.*")],
    )
    raiz.destroy()
    return ruta


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe un .mp3 (u otro audio) a un archivo .txt usando Whisper.")
    parser.add_argument("audio", nargs="?",
                        help="archivo de audio (.mp3, .wav, .m4a...). "
                             "Si no se pasa, se abre una ventana para elegirlo.")
    parser.add_argument("-o", "--salida",
                        help="archivo .txt de salida (por defecto: mismo nombre que el audio)")
    parser.add_argument("-m", "--modelo", default="small", choices=MODELOS,
                        help="tamano del modelo: mas grande = mas preciso pero mas lento "
                             "(por defecto: small)")
    parser.add_argument("-i", "--idioma", default="es",
                        help="codigo de idioma (por defecto: es = espanol). "
                             "Otros: en, pt... o 'auto' para detectarlo solo.")
    parser.add_argument("-t", "--tiempos", action="store_true",
                        help="incluir marcas de tiempo [mm:ss - mm:ss] en cada linea")
    parser.add_argument("--gpu", action="store_true",
                        help="usar GPU NVIDIA (CUDA) si esta disponible")
    args = parser.parse_args()

    ruta = args.audio
    if not ruta:
        ruta = elegir_archivo_con_ventana()
        if not ruta:
            print("No se eligio ningun archivo.")
            return

    transcribir(ruta, args.salida, args.modelo, args.idioma, args.tiempos, args.gpu)


if __name__ == "__main__":
    main()
