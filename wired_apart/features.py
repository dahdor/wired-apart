"""Ingeniería de variables: cohortes, tasas, normalizaciones, índices derivados.

Funciones puras (no I/O). Los notebooks orquestan la lectura/escritura.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# --- Cohort assignment --------------------------------------------------------
# El libro (Haidt 2024) define cohortes por año de nacimiento. Para nuestros
# datos de encuestas por año, asignamos cohorte restando la edad modal/mediana
# del año de la encuesta.

def assign_birth_cohort(year_col: pd.Series, age_col: pd.Series) -> pd.Series:
    """Calcula cohorte de nacimiento = año_encuesta - edad."""
    return (year_col - age_col).astype("Int64")


# --- Periodization of the "Great Rewiring" -----------------------------------
# Haidt y Twenge ubican la "Gran Reconexión" entre 2010 y 2015. Construimos una
# etiqueta de período para segmentar el análisis.

PERIOD_BINS = [-np.inf, 2009, 2014, 2019, np.inf]
PERIOD_LABELS = ["pre-rewiring (≤2009)", "rewiring (2010-2014)", "post-rewiring (2015-2019)", "pandemic-era (≥2020)"]


def assign_rewiring_period(year_col: pd.Series) -> pd.Series:
    """Etiqueta cada observación según el período de la Gran Reconexión."""
    return pd.cut(year_col, bins=PERIOD_BINS, labels=PERIOD_LABELS, right=True)


# --- Normalization & rates ----------------------------------------------------
def rate_per_100k(count: pd.Series, population: pd.Series) -> pd.Series:
    """Tasa por cada 100 000 habitantes. Maneja population=0 → NaN."""
    return count.div(population.replace(0, np.nan)) * 1e5


def zscore(s: pd.Series) -> pd.Series:
    """Z-score robusto: (x - median) / IQR. Útil para outliers severos."""
    q25, q50, q75 = s.quantile([0.25, 0.5, 0.75])
    iqr = q75 - q25
    if iqr == 0:
        return s * 0
    return (s - q50) / iqr
