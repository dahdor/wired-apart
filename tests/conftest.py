"""Fixtures compartidos para la suite de tests.

Las pruebas son estructuralmente importantes para reproducibilidad: detectan
silenciosamente cuando una refactorización cambia las propiedades estadísticas
del dataset (e.g., una media ponderada que cambia por un cambio de tipos).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from wired_apart import config


@pytest.fixture(scope="session")
def yrbs_clean() -> pd.DataFrame:
    """yrbs_clean_2005_2021.parquet como DataFrame inmutable."""
    path = config.PROCESSED_DIR / "yrbs_clean_2005_2021.parquet"
    if not path.exists():
        pytest.skip(
            f"Falta {path}. Ejecute el pipeline (`make pipeline`) "
            "o restaure desde git."
        )
    return pd.read_parquet(path)


@pytest.fixture(scope="session")
def yrbs_raw() -> pd.DataFrame:
    """yrbs_2005_2021.parquet (stacked raw) como DataFrame."""
    path = config.PROCESSED_DIR / "yrbs_2005_2021.parquet"
    if not path.exists():
        pytest.skip(
            f"Falta {path}. Ejecute el pipeline o restaure desde git."
        )
    return pd.read_parquet(path)


@pytest.fixture(scope="session")
def wonder() -> pd.DataFrame:
    """wonder_clean_2005_2024.csv como DataFrame."""
    path = config.PROCESSED_DIR / "wonder_clean_2005_2024.csv"
    if not path.exists():
        pytest.skip(f"Falta {path}.")
    return pd.read_csv(path)


@pytest.fixture(scope="session")
def project_root() -> Path:
    return config.PROJECT_ROOT
