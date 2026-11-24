"""Configuración centralizada del registro de eventos y errores.

El log es el único mecanismo de persistencia del proyecto (no hay base de
datos). La ruta se calcula a partir de la ubicación de este archivo para que
funcione igual al ejecutar ``main.py``, ``menu.py`` o cualquier módulo desde
otra carpeta.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------------------------
# Rutas absolutas: evita depender del directorio actual de trabajo.
# ---------------------------------------------------------------------------
RAIZ = os.path.dirname(os.path.abspath(__file__))
DIRECTORIO_LOGS = os.path.join(RAIZ, "logs")
ARCHIVO_LOG = os.path.join(DIRECTORIO_LOGS, "sistema.log")
MAXIMO_BYTES = 1_000_000  # Rotación a 1 MB para que el archivo no crezca sin límite.
COPIAS = 3


def configurar_consola():
    """Fuerza UTF-8 en la consola de Windows para evitar UnicodeEncodeError."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")


configurar_consola()
os.makedirs(DIRECTORIO_LOGS, exist_ok=True)

logger = logging.getLogger("SoftwareFJ")
logger.setLevel(logging.INFO)
# Evitamos que el mensaje se duplique si otro módulo configura logging después.
logger.propagate = False

# Solo agregamos el manejador una vez: el módulo puede importarse desde muchos
# archivos distintos y no queremos líneas repetidas en el log.
if not logger.handlers:
    manejador = RotatingFileHandler(
        ARCHIVO_LOG,
        maxBytes=MAXIMO_BYTES,
        backupCount=COPIAS,
        encoding="utf-8",
    )
    manejador.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(manejador)


def registrar_evento(mensaje):
    """Registra un evento normal de la operación del sistema."""
    logger.info(mensaje)


def registrar_error(mensaje):
    """Registra un error ya controlado y descrito por quien lo lanza."""
    logger.error(mensaje)


def registrar_excepcion(mensaje, error):
    """Registra una excepción con su traza completa para facilitar el diagnóstico."""
    logger.error(
        "%s | %s: %s",
        mensaje,
        type(error).__name__,
        error,
        exc_info=True,  # Dentro de un except incluye la pila de llamadas.
    )
