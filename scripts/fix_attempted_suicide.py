"""Fix #1 (CHANGELOG): attempted_suicide_yesno estaba invertido para 2011-2021.

Aplica el mapeo correcto a partir del stacked raw sin necesidad del driver ODBC:
- 2005, 2007: Q22 binario (1=Yes, 2=No)
- 2009, 2011, 2013, 2015, 2017, 2019, 2021: ordinal (1=0 times=No, 2+=Yes)

Referencia: YRBS codebooks oficiales, revisión jun-2026.
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from wired_apart import config, force_utf8_stdout
from wired_apart.dataset import YRBS_QCODE_CROSSWALK

# Reconfigurar stdout/stderr a UTF-8 para que caracteres como í se
# impriman correctamente en Windows.
force_utf8_stdout()

# Cargar el stacked raw (no requiere ODBC)
raw = pd.read_parquet(config.PROCESSED_DIR / "yrbs_2005_2021.parquet")
clean = pd.read_parquet(config.PROCESSED_DIR / "yrbs_clean_2005_2021.parquet")

# Diagnóstico: estado actual
print("=== ANTES ===")
for y in sorted(clean["year"].unique()):
    sub = clean[clean["year"] == y]
    n_yes = (sub["attempted_suicide_yesno"] * sub["weight"]).sum() / sub["weight"].sum() * 100
    n = sub["attempted_suicide_yesno"].notna().sum()
    print(f"  {y}: attempted_suicide_yesno (ponderado) = {n_yes:.1f}%  (n válidos: {n})")

# Reconstruir attempted_suicide_yesno y ordinal con el mapeo correcto
# Importante: usar el stacked raw para no perder el peso de cada año
new_yesno = np.full(len(clean), np.nan)
new_ordinal = np.full(len(clean), np.nan)

for year, mapping in YRBS_QCODE_CROSSWALK.items():
    q = mapping["attempted_suicide"]
    if q not in raw.columns:
        continue
    # Seleccionar las filas de este año en clean
    clean_year_mask = (clean["year"] == year).values
    # Y las filas correspondientes en raw (mismo orden, ya que clean se construyó
    # recorriendo años)
    raw_year_mask = (raw["year"] == year).values
    if year in (2005, 2007):
        # Binario 1=Yes, 2=No
        yesno_year = raw.loc[raw_year_mask, q].map({1.0: 1, 2.0: 0})
    else:
        # Ordinal 1=0 times (No), 2+=Yes
        yesno_year = (raw.loc[raw_year_mask, q] >= 2).astype("float64")
        yesno_year[raw.loc[raw_year_mask, q].isna()] = np.nan
    # Si clean fue construido recorriendo años en el mismo orden, los índices
    # deben coincidir. Verificamos con un assert.
    assert yesno_year.shape[0] == clean_year_mask.sum(), (
        f"Mismatch año {year}: raw={raw_year_mask.sum()}, clean={clean_year_mask.sum()}"
    )
    new_yesno[clean_year_mask] = yesno_year.values
    if year != 2005 and year != 2007:
        new_ordinal[clean_year_mask] = raw.loc[raw_year_mask, q].values

# Sobreescribir
clean["attempted_suicide_yesno"] = new_yesno
clean["attempted_suicide_ordinal"] = new_ordinal

# Diagnóstico: estado nuevo
print("\n=== DESPUÉS ===")
for y in sorted(clean["year"].unique()):
    sub = clean[clean["year"] == y]
    valid = sub.dropna(subset=["attempted_suicide_yesno"])
    if len(valid) == 0:
        continue
    n_yes = (valid["attempted_suicide_yesno"] * valid["weight"]).sum() / valid["weight"].sum() * 100
    n = len(valid)
    print(f"  {y}: attempted_suicide_yesno (ponderado) = {n_yes:.1f}%  (n válidos: {n})")

# Guardar
out = config.PROCESSED_DIR / "yrbs_clean_2005_2021.parquet"
clean.to_parquet(out, index=False)
print(f"\nGuardado: {out}")
print(f"Filas: {len(clean):,}, columnas: {clean.shape[1]}")
