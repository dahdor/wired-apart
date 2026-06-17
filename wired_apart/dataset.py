"""Carga y validación de los datasets crudos (MTF, NSDUH).

Funciones de soporte usadas por los notebooks. Mantener este módulo liviano:
cualquier transformación pesada va en `features.py`.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from wired_apart import config


def sha256_of(path: Path, chunk_size: int = 1 << 20) -> str:
    """Devuelve el hash SHA-256 de un archivo. Útil para reproducibilidad."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_columns(df: pd.DataFrame, expected: list[str], source: str) -> None:
    """Falla rápido si el dataset no tiene las columnas mínimas esperadas."""
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(
            f"[{source}] Faltan columnas esperadas: {missing}\n"
            f"Columnas disponibles: {list(df.columns)}"
        )


def load_mtf(path: Path | None = None) -> pd.DataFrame:
    """Carga el dataset de Monitoring the Future desde `data/raw/`."""
    path = path or (config.RAW_DIR / "mtf" / "mtf_public_use.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo MTF en {path}. "
            "Verifica la descarga en data/raw/mtf/."
        )
    # MTF se publica en distintos formatos (.sav, .dta, .csv). pyreadstat
    # detecta el formato por extensión.
    if path.suffix in {".sav", ".dta"}:
        import pyreadstat

        df, _meta = pyreadstat.read_file(str(path))
    else:
        df = pd.read_csv(path, low_memory=False)
    return df


def load_nsduh(path: Path | None = None) -> pd.DataFrame:
    """Carga el dataset NSDUH desde `data/raw/`."""
    path = path or (config.RAW_DIR / "nsduh" / "nsduh_public_use.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo NSDUH en {path}. "
            "Verifica la descarga en data/raw/nsduh/."
        )
    if path.suffix in {".sas7bdat", ".sav", ".dta"}:
        import pyreadstat

        df, _meta = pyreadstat.read_file(str(path))
    else:
        df = pd.read_csv(path, low_memory=False)
    return df
