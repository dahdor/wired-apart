"""wired-apart: Análisis de la asociación entre la transición digital y el bienestar adolescente.

Este paquete contiene utilidades de soporte para el pipeline de análisis:
    - config: rutas y constantes globales
    - dataset: funciones de carga y descarga de datos crudos
    - features: ingeniería de variables (tasas, cohortes, normalizaciones)
    - plots: utilidades de visualización con la paleta del proyecto
"""
from __future__ import annotations

import sys

__version__ = "0.1.0"


def force_utf8_stdout() -> None:
    """Reconfigura stdout/stderr a UTF-8 para soportar Unicode en Windows.

    En Windows, el code page por defecto de la consola es cp1252 (alias
    ``charmap``), que no puede representar caracteres como ``✓`` ``í``
    ``→`` ``…``. Cualquier script que imprima esos caracteres a stdout
    lanza::

        UnicodeEncodeError: 'charmap' codec can't encode character '\\u2713'

    Llamar a esta función al inicio del script fija la codificación a
    UTF-8, que sí soporta todo el rango Unicode. En Linux/macOS es un
    no-op porque el code page ya es UTF-8.

    No retorna nada. Es seguro llamarla más de una vez (idempotente).

    Notas
    -----
    - ``sys.stdout.reconfigure`` requiere Python 3.7+; el proyecto
      requiere 3.12, así que siempre está disponible.
    - ``errors="replace"`` evita que un byte corrupto aborte el script;
      preferimos un ``?`` en consola a un crash.
    - GitHub Actions Windows ya fija ``PYTHONIOENCODING=utf-8`` en sus
      runners por defecto, así que allí no falla. El fix es para
      terminales Windows interactivas (PowerShell, cmd, Windows
      Terminal) y para ``subprocess`` que hereda el code page del
      padre.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            # Python < 3.7 (no aplica al proyecto) o stream exótico.
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            # Stream no reconfigurable (p.ej. capturado por pytest con
            # captura de stdout). No es fatal.
            pass
