"""Fix hispanic_yesno para 2005 (auditoría externa 2026-06-18).

Hallazgo
--------
En 2005, la pregunta Q4 (origen hispano) tenía **8 categorías**:
    1 = Mexican
    2 = Puerto Rican
    3 = Central or South American
    4 = Cuban
    5 = Other Hispanic
    6 = Not Hispanic
    7 = Multiple Hispanic
    8 = Unknown

El cleaning original (notebook 1.0, celda 42) usaba
``sub['q4'].map({1.0: 1, 2.0: 0})`` para todos los años. En 2007+ q4 es
binario (1=Yes, 2=No) y el mapeo es correcto, pero en 2005 q4 tiene 8
categorías y el mapeo deja 3, 4, 5, 6, 7, 8 como NaN. Resultado: 96.3%
de los registros de 2005 quedan con ``hispanic_yesno = NaN`` en
``yrbs_clean_2005_2021.parquet``.

Corrección
----------
Reconstruir ``hispanic_yesno`` con la lógica específica por año:
    - 2005:   {1,2,3,4,5,7} -> 1 (Yes), {6} -> 0 (No), {8} -> NaN (Unknown)
    - 2007+:  {1} -> 1, {2} -> 0 (binario CDC)

Re-ejecutable sin ODBC. Sobrescribe el parquet.
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from wired_apart import config

# Mapeo de 2005 (8-cat → binario) según YRBS 2005 codebook
HISPANIC_2005_MAP = {
    1.0: 1,  # Mexican
    2.0: 1,  # Puerto Rican
    3.0: 1,  # Central or South American
    4.0: 1,  # Cuban
    5.0: 1,  # Other Hispanic
    6.0: 0,  # Not Hispanic
    7.0: 1,  # Multiple Hispanic
    8.0: np.nan,  # Unknown
}

# Mapeo para 2007+ (binario)
HISPANIC_BINARY_MAP = {1.0: 1, 2.0: 0}


def main() -> int:
    path = config.PROCESSED_DIR / "yrbs_clean_2005_2021.parquet"
    print(f"Leyendo: {path}")
    df = pd.read_parquet(path)
    print(f"Shape: {df.shape}")

    # Estado actual
    print("\n=== ANTES ===")
    for y in sorted(df["year"].unique()):
        sub = df[df["year"] == y]
        n = sub["hispanic_yesno"].notna().sum()
        n_yes = (sub["hispanic_yesno"] == 1).sum()
        n_no = (sub["hispanic_yesno"] == 0).sum()
        n_nan = sub["hispanic_yesno"].isna().sum()
        print(
            f"  {y}: total={len(sub):5d}  "
            f"Yes={n_yes:5d} ({100*n_yes/len(sub):.1f}%)  "
            f"No={n_no:5d} ({100*n_no/len(sub):.1f}%)  "
            f"NaN={n_nan:5d} ({100*n_nan/len(sub):.1f}%)"
        )

    # Aplicar corrección
    # La columna `hispanic` (raw) preserva la codificación original por año:
    #   2005:  1-8 (origen hispano detallado)
    #   2007+: 1-2 (binario Yes/No)
    new_hy = np.full(len(df), np.nan)
    for year in df["year"].unique():
        year_int = int(year)
        mapping = HISPANIC_2005_MAP if year_int == 2005 else HISPANIC_BINARY_MAP
        mask = (df["year"] == year).values
        new_hy[mask] = df.loc[mask, "hispanic"].map(mapping).values
    df["hispanic_yesno"] = new_hy

    # Estado nuevo
    print("\n=== DESPUÉS ===")
    for y in sorted(df["year"].unique()):
        sub = df[df["year"] == y]
        n = sub["hispanic_yesno"].notna().sum()
        n_yes = (sub["hispanic_yesno"] == 1).sum()
        n_no = (sub["hispanic_yesno"] == 0).sum()
        n_nan = sub["hispanic_yesno"].isna().sum()
        print(
            f"  {y}: total={len(sub):5d}  "
            f"Yes={n_yes:5d} ({100*n_yes/len(sub):.1f}%)  "
            f"No={n_no:5d} ({100*n_no/len(sub):.1f}%)  "
            f"NaN={n_nan:5d} ({100*n_nan/len(sub):.1f}%)"
        )

    # Guardar
    df.to_parquet(path, index=False)
    print(f"\nSobrescrito: {path}")
    print(f"Filas: {len(df):,}, columnas: {df.shape[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
