"""Carga y validación de los datasets crudos y procesados (YRBS, NCHS/WONDER).

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


def load_yrbs_processed(path: Path | None = None) -> pd.DataFrame:
    """Carga el stacked YRBS (9 años) desde `data/processed/yrbs_2005_2021.parquet`.

    Este es el archivo que produce el notebook 0.0-dh-data-acquisition.
    Usar este loader en lugar de `load_yrbs` para evitar la dependencia de
    pyodbc en cada lectura.

    Returns
    -------
    pd.DataFrame
        134,674 registros × 230 columnas, con una columna `year` (2005-2021)
        y todas las q-vars del cuestionario original en formato float64
        (NaN donde no aplica).
    """
    path = path or (config.PROCESSED_DIR / "yrbs_2005_2021.parquet")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo procesado en {path}. "
            "Ejecuta notebooks/0.0-dh-data-acquisition.ipynb primero."
        )
    return pd.read_parquet(path)


# Crosswalk: en YRBS, los Q-codes rotan cada 2 años para evitar priming
# effects, pero la redacción de las preguntas clave se mantiene estable.
# Este mapeo fue validado empíricamente comparando las distribuciones
# (% yes) entre años contra los codebooks oficiales.
# Documentado en notebooks/1.0-dh-yrbs-cleaning.ipynb.
YRBS_QCODE_CROSSWALK: dict[int, dict[str, str]] = {
    2005: {
        "sad_hopeless": "q23",
        "considered_suicide": "q24",
        "made_plan": "q25",
        "attempted_suicide": "q22",  # 0/1+ veces (ordinal en algunas preguntas)
        "electronically_bullied": "q21",
        "bullied_school": "q20",
    },
    2007: {
        "sad_hopeless": "q23",
        "considered_suicide": "q24",
        "made_plan": "q25",
        "attempted_suicide": "q22",
        "electronically_bullied": "q21",
        "bullied_school": "q20",
    },
    2009: {
        "sad_hopeless": "q23",
        "considered_suicide": "q24",
        "made_plan": "q25",
        "attempted_suicide": "q26",  # 0/1/2-3/4-5/6+ veces
        "electronically_bullied": "q22",
        "bullied_school": "q21",
    },
    2011: {
        "sad_hopeless": "q24",
        "considered_suicide": "q25",
        "made_plan": "q26",
        "attempted_suicide": "q27",
        "electronically_bullied": "q23",
        "bullied_school": "q22",
    },
    2013: {
        "sad_hopeless": "q26",
        "considered_suicide": "q27",
        "made_plan": "q28",
        "attempted_suicide": "q29",  # verificar con codebook 2013
        "electronically_bullied": "q25",
        "bullied_school": "q24",
    },
    2015: {
        "sad_hopeless": "q26",
        "considered_suicide": "q27",
        "made_plan": "q28",
        "attempted_suicide": "q29",  # verificar con codebook 2015
        "electronically_bullied": "q25",
        "bullied_school": "q24",
    },
    2017: {
        "sad_hopeless": "q25",
        "considered_suicide": "q26",
        "made_plan": "q27",
        "attempted_suicide": "q28",
        "electronically_bullied": "q24",
        "bullied_school": "q23",
        "screen_time": "q80",  # en 2017 Q80 = "watch TV only" (no incluye social media)
    },
    2019: {
        "sad_hopeless": "q25",
        "considered_suicide": "q26",
        "made_plan": "q27",
        "attempted_suicide": "q28",
        "electronically_bullied": "q24",
        "bullied_school": "q23",
        # Q80 en 2019 = "video or computer games or computer not for school work,
        # including texting and social media" — ESTA es la métrica de Haidt
        "screen_time": "q80",
    },
    2021: {
        "sad_hopeless": "q25",
        "considered_suicide": "q26",
        "made_plan": "q27",
        "attempted_suicide": "q28",
        "electronically_bullied": "q24",
        "bullied_school": "q23",
        # Q80 en 2021 = "sports teams" — NO es screen time
        # No hay screen time válido en 2021
    },
}


def load_wonder(path: Path | None = None) -> pd.DataFrame:
    """Carga la extracción de CDC WONDER (suicidio adolescente) desde `data/raw/cdc/`."""
    path = path or (config.RAW_DIR / "cdc" / "wonder_suicide_adolescent.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo WONDER en {path}. "
            "Verifica la descarga en data/raw/cdc/."
        )
    return pd.read_csv(path, low_memory=False)


def load_wonder_processed(path: Path | None = None) -> pd.DataFrame:
    """Carga la mortalidad adolescente (suicidio) desde NCHS Socrata,
    procesada en `data/processed/wonder_suicide_adolescent_2018_2024.csv`.

    Esta es la serie de mortalidad 2018-2024 que produce el notebook 0.0.
    Para 2005-2017 ver limitations: el WONDER API no respondió durante la
    fase de adquisición y se optó por declarar el rango disponible.
    """
    path = path or (config.PROCESSED_DIR / "wonder_suicide_adolescent_2018_2024.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo procesado en {path}. "
            "Ejecuta notebooks/0.0-dh-data-acquisition.ipynb primero."
        )
    return pd.read_csv(path)
