#!/usr/bin/env bash
# Transcribe un audio a .txt sin tener que preocuparse por Python ni venvs.
#
# Uso:
#   ./transcribir.sh                 -> transcribe el archivo de ARCHIVO (abajo)
#   ./transcribir.sh /ruta/otro.mp3  -> transcribe ese otro archivo
#
# La primera vez crea el entorno (.venv) e instala todo; puede tardar unos
# minutos. Las siguientes veces arranca directo.

# ===== Cambiá esta ruta por la del audio a transcribir =====
ARCHIVO="/ruta/absoluta/al/audio.mp3"
# ===========================================================

set -e

# Trabajar siempre en la carpeta del proyecto, se llame desde donde se llame.
cd "$(dirname "$0")"

AUDIO="${1:-$ARCHIVO}"
if [ ! -f "$AUDIO" ]; then
    echo "ERROR: no encuentro el archivo de audio:"
    echo "  $AUDIO"
    echo "Abrí transcribir.sh y cambiá la línea ARCHIVO=\"...\" por la ruta correcta."
    exit 1
fi

# Python del venv: en Linux/Mac está en bin/, en Windows (Git Bash) en Scripts/.
python_del_venv() {
    if [ -x .venv/bin/python ]; then
        echo .venv/bin/python
    elif [ -x .venv/Scripts/python.exe ]; then
        echo .venv/Scripts/python.exe
    fi
}

# Busca un Python 3.10+ que funcione de verdad (en Windows "python3" a veces
# es un acceso directo a la Microsoft Store que no hace nada).
buscar_python() {
    for cmd in python3 python py; do
        if command -v "$cmd" >/dev/null 2>&1 &&
           "$cmd" -c 'import sys; sys.exit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
            echo "$cmd"
            return
        fi
    done
}

PY="$(python_del_venv)"

if [ -z "$PY" ]; then
    SISTEMA_PY="$(buscar_python)"
    if [ -z "$SISTEMA_PY" ]; then
        echo "ERROR: no encontré Python 3.10 o más nuevo instalado."
        echo "Instalalo desde https://www.python.org/downloads/ y volvé a correr este script."
        exit 1
    fi
    echo "Creando el entorno (.venv) con $SISTEMA_PY..."
    if ! "$SISTEMA_PY" -m venv .venv; then
        rm -rf .venv
        echo "ERROR: no se pudo crear el entorno."
        echo "En Ubuntu/Debian instalá el paquete: sudo apt install python3-venv"
        exit 1
    fi
    PY="$(python_del_venv)"
fi

# Instalar las librerías si faltan (primera vez, o si una instalación anterior
# quedó a medias).
if ! "$PY" -c 'import faster_whisper' >/dev/null 2>&1; then
    echo "Instalando las librerías (solo la primera vez, puede tardar)..."
    "$PY" -m pip install --upgrade pip
    "$PY" -m pip install -r requirements.txt
    "$PY" -m pip install faster-whisper --no-deps
fi

"$PY" transcribir.py "$AUDIO"
