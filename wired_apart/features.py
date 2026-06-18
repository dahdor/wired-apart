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
# Haidt (2024, ch.1) and Twenge (2017) date the Great Rewiring to 2010-2015:
# the period in which the smartphone became ubiquitous among teens and play-
# based childhood was replaced by phone-based childhood.
# We segment the analysis into 4 mutually exclusive periods, with the rewiring
# window INCLUDING 2015 (per Haidt) — this is a fixed boundary, not a year
# boundary. Bins use right=True so the upper edge is inclusive.
#
# Pre-rewiring  (≤2009)  : 5 years of "before"
# Rewiring      (2010-2015): the Great Rewiring itself
# Post-rewiring  (2016-2019): 4 years of "after", pre-COVID
# Pandemic-era  (≥2020)  : COVID叠加 and beyond

from wired_apart import config

PERIOD_BINS = [
    -np.inf,
    config.REWIRING_START_YEAR - 1,   # 2009
    config.REWIRING_END_YEAR,         # 2015
    2019,
    np.inf,
]
PERIOD_LABELS = [
    "pre-rewiring (≤2009)",
    "rewiring (2010-2015)",
    "post-rewiring (2016-2019)",
    "pandemic-era (≥2020)",
]


def assign_rewiring_period(year_col: pd.Series) -> pd.Series:
    """Etiqueta cada observación según el período de la Gran Reconexión.

    La ventana "rewiring" sigue a Haidt (2024) e incluye 2015.
    """
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
