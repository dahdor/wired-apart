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


def load_yrbs(path: Path | None = None, year: int | None = None) -> pd.DataFrame:
    """Carga un año del dataset YRBS desde `data/raw/yrbs/`.

    El dataset se distribuye en formato Access (.mdb) y se lee con pyodbc
    usando el driver ODBC de Microsoft Access (incluido en Windows).
    Alternativa: usar read_table con mdbtools en Linux/macOS.

    Para convertir a CSV/Parquet una vez (y no depender de pyodbc en cada
    lectura), ver `notebooks/0.0-dh-data-acquisition.ipynb`.
    """
    if path is None:
        if year is None:
            raise ValueError("Provide either `path` or `year`.")
        path = config.RAW_DIR / "yrbs" / f"yrbs{year}.mdb"
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo YRBS en {path}. "
            "Verifica la descarga en data/raw/yrbs/."
        )
    import pyodbc

    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={path};"
    )
    conn = pyodbc.connect(conn_str)
    try:
        df = pd.read_sql("SELECT * FROM [XXHq]", conn)
    finally:
        conn.close()
    return df


def load_wonder(path: Path | None = None) -> pd.DataFrame:
    """Carga la extracción de CDC WONDER (suicidio adolescente) desde `data/raw/cdc/`."""
    path = path or (config.RAW_DIR / "cdc" / "wonder_suicide_adolescent.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo WONDER en {path}. "
            "Verifica la descarga en data/raw/cdc/."
        )
    return pd.read_csv(path, low_memory=False)
