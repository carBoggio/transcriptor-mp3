# Transcriptor MP3 → TXT (español)

Programa en Python que recibe un audio (`.mp3`, también `.wav`, `.m4a`, `.ogg`...) y genera un `.txt` con la transcripción.
Por defecto transcribe en **español**.

Usa **Whisper** (el modelo de reconocimiento de voz de OpenAI) mediante la librería [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper).
Todo corre **en tu PC**: no hace falta cuenta, clave ni internet (solo la primera vez, para descargar el modelo).
No hace falta instalar `ffmpeg`.

---

## 1. Instalar Python (una sola vez)

1. Descargá Python 3.10 o más nuevo desde <https://www.python.org/downloads/windows/>.
2. En el instalador **tildá "Add python.exe to PATH"** y dale *Install Now*.
3. Abrí **CMD** o **PowerShell** y verificá:
   ```
   python --version
   ```

## 2. Descargar este programa

- Botón verde **Code → Download ZIP** en GitHub y descomprimilo, **o**
- con git: `git clone https://github.com/carBoggio/transcriptor-mp3.git`

## 3. Instalar la librería (una sola vez)

En CMD/PowerShell, dentro de la carpeta del programa:

```
cd ruta\a\transcriptor-mp3
python -m pip install -r requirements.txt
python -m pip install faster-whisper --no-deps
```

Son **dos comandos**: así funciona en cualquier Python de 3.10 a 3.15.
(En Python 3.15 `onnxruntime` todavía no existe para Windows; el programa funciona igual, solo que sin el filtro de silencios.)

## 4. Usarlo desde CMD o PowerShell

```
python transcribir.py "C:\Users\yo\Music\audio.mp3"
```

Se genera `audio.txt` en la misma carpeta que el audio.

Opciones:

| Opción | Qué hace | Ejemplo |
|---|---|---|
| `-o archivo.txt` | Elegir dónde guardar el `.txt` | `-o C:\textos\clase1.txt` |
| `-m modelo` | Tamaño del modelo: `tiny`, `base`, `small` (por defecto), `medium`, `large-v3`, `turbo` | `-m medium` |
| `-i idioma` | Idioma del audio. Por defecto `es` (español). `auto` = lo detecta solo | `-i en` |
| `-t` | Agrega marcas de tiempo `[mm:ss - mm:ss]` a cada línea | `-t` |
| `--gpu` | Usa la placa de video NVIDIA si hay (mucho más rápido) | `--gpu` |

Ejemplos:

```
python transcribir.py entrevista.mp3 -m medium
python transcribir.py clase.mp3 -o clase.txt -t
```

Ver la ayuda: `python transcribir.py -h`

> En PowerShell, si la ruta tiene espacios, ponela entre comillas.

## 5. Usarlo desde Thonny

1. Abrí Thonny → **Herramientas → Administrar paquetes…** → buscá `faster-whisper` → **Instalar**.
2. Abrí `transcribir.py` y apretá **F5** (Run).
3. Se abre una ventana para elegir el `.mp3`. El `.txt` se guarda al lado del audio.

Para pasarle opciones en Thonny: **Ver → Argumentos del programa** y escribí, por ejemplo, `audio.mp3 -m medium`.

## ¿Qué modelo elijo?

| Modelo | Precisión | Velocidad (CPU) | Descarga |
|---|---|---|---|
| `tiny` / `base` | baja | muy rápido | ~75–150 MB |
| `small` (por defecto) | buena | ~6x tiempo real* | ~480 MB |
| `medium` | muy buena | lento | ~1.5 GB |
| `large-v3` | la mejor | muy lento en CPU (ideal con `--gpu`) | ~3 GB |
| `turbo` | casi como large, más rápido | medio | ~1.6 GB |

\* Probado: un audio de 41 minutos en español tardó unos 7 minutos con `small` en una CPU Ryzen 7.

Los modelos se descargan solos la primera vez y quedan guardados (`C:\Users\<vos>\.cache\huggingface`).

## Problemas comunes

- **`python` no se reconoce**: reinstalá Python tildando *Add to PATH*, o usá `py` en vez de `python`.
- **`No module named faster_whisper`**: corré los dos comandos del paso 3 (o instalalo desde Thonny).
- **`ResolutionImpossible` / `onnxruntime` al instalar**: pasa con Python 3.15 si instalás `faster-whisper` directo. Usá los dos comandos del paso 3.
- **`--gpu` no funciona**: requiere placa NVIDIA con drivers y librerías CUDA 12 / cuDNN 9; si falla, el programa sigue con CPU automáticamente.
