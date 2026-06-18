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

    Este es el stacked raw de 9 años producido por `notebooks/0.0-dh-data-acquisition`.
    Contiene TODAS las q-vars del codebook original (q1-q99) más las columnas
    derivadas de CDC (`raceeth`, `raceorig`, `weight`, `stratum`, `psu`).

    Usar este loader en lugar de `load_yrbs` para evitar la dependencia de pyodbc
    en cada lectura.

    Returns
    -------
    pd.DataFrame
        134,674 registros × 230 columnas (stacked raw), con una columna `year`
        (2005-2021) y todas las q-vars del cuestionario original en formato
        float64 (NaN donde no aplica).

    Para el dataset limpio (15 columnas, con crosswalk aplicado), usar
    `load_yrbs_clean`.
    """
    path = path or (config.PROCESSED_DIR / "yrbs_2005_2021.parquet")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo procesado en {path}. "
            "Ejecuta notebooks/0.0-dh-data-acquisition.ipynb primero."
        )
    return pd.read_parquet(path)


def load_yrbs_clean(path: Path | None = None) -> pd.DataFrame:
    """Carga el YRBS limpio y unificado (9 años) desde
    `data/processed/yrbs_clean_2005_2021.parquet`.

    Este es el output de `notebooks/1.0-dh-yrbs-cleaning`. Contiene 15 columnas
    con nombres semánticos (no q-codes), producidas aplicando el YRBS_QCODE_CROSSWALK.

    Returns
    -------
    pd.DataFrame
        134,674 registros × 15 columnas: `year`, `age`, `sex`, `grade`,
        `hispanic` (categórico: 1=Yes / 2=No para 2007+; 8 cats para 2005),
        `hispanic_yesno` (1=Yes / 0=No unificado para todos los años),
        `race` (8 cats, derivado de CDC `raceeth`), `weight`, `stratum`, `psu`,
        `sad_hopeless`, `considered_suicide`, `made_plan`,
        `attempted_suicide_yesno`, `attempted_suicide_ordinal`, `screen_time`.
    """
    path = path or (config.PROCESSED_DIR / "yrbs_clean_2005_2021.parquet")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo limpio en {path}. "
            "Ejecuta notebooks/1.0-dh-yrbs-cleaning.ipynb primero."
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
    """Carga la mortalidad adolescente (suicidio) limpia y combinada,
    desde `data/processed/wonder_clean_2005_2024.csv`.

    Este archivo se produce en `notebooks/1.1-dh-wonder-cleaning` combinando:
    - NCHS Socrata 2018-2024 (28 filas con IC95%).
    - NCHS Health, United States 2018 Table 9 (PDF público), 12 filas para
      2010/2016/2017 (sin IC95%).

    Returns
    -------
    pd.DataFrame
        40 filas × 9 columnas: `year`, `sex_age`, `sex`, `rate_per_100k`,
        `se`, `lci`, `uci`, `estimate_type`, `source` (Socrata | HUS2018).

    Gaps documentados: 2005-2009 y 2011-2015. El CDC WONDER API
    (D76/D77/D158/D176) rechaza queries programáticas con HTTP 400, por lo
    que no se pudo automatizar la descarga de esos años. Ver
    `references/data_provenance.md` para detalle.
    """
    path = path or (config.PROCESSED_DIR / "wonder_clean_2005_2024.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo procesado en {path}. "
            "Ejecuta notebooks/1.1-dh-wonder-cleaning.ipynb primero."
        )
    return pd.read_csv(path)


def load_wonder_socrata_only(path: Path | None = None) -> pd.DataFrame:
    """Carga solo la parte de NCHS Socrata (2018-2024, 28 filas, con IC95%).

    Útil cuando se quiere análisis restringido a Socrata (sin los puntos
    HUS que no tienen IC).
    """
    path = path or (config.PROCESSED_DIR / "wonder_suicide_adolescent_2018_2024.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo Socrata en {path}. "
            "Ejecuta notebooks/0.0-dh-data-acquisition.ipynb primero."
        )
    return pd.read_csv(path)
