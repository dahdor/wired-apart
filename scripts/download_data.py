"""Descarga automatizada de los datos crudos de YRBS y NCHS Socrata.

Este script elimina la dependencia de colocar manualmente los archivos .mdb en
`data/raw/yrbs/`. Es idempotente: si los archivos ya están en disco con el
SHA-256 esperado, no los re-descarga.

Fuentes:
- YRBS (9 años, 2005-2021): CDC distribuye cada año como .zip que contiene un
  .mdb (Microsoft Access). Se descarga, descomprime, y se verifica el SHA-256
  contra el catálogo en `references/data_provenance.md`.
- NCHS Socrata (wonder_suicide_adolescent_2018-2024): API pública de
  data.cdc.gov. Se consulta por HTTP y se guarda en CSV.

Los archivos PDF de referencia (NCHS HUS 2018 Table 9, NCHS Data Brief 471)
**ya están commiteados** en `data/external/`, así que este script no los
descarga.

Uso:
    uv run python scripts/download_data.py            # todos los años
    uv run python scripts/download_data.py --year 2019  # solo un año
    uv run python scripts/download_data.py --force      # re-descargar aunque exista
    uv run python scripts/download_data.py --socrata-only  # solo NCHS Socrata

Requisitos: solo requests (ya en pyproject.toml).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from wired_apart import config
from wired_apart.dataset import sha256_of

# Catálogo de URLs de YRBS. Mantenido en sincronía con
# references/data_provenance.md (esos SHA-256 son los "ground truth" que
# validamos aquí).
YRBS_URLS = {
    2005: "https://www.cdc.gov/yrbs/files/2005/yrbs2005.zip",
    2007: "https://www.cdc.gov/yrbs/files/2007/yrbs2007.zip",
    2009: "https://www.cdc.gov/yrbs/files/2009/yrbs2009.zip",
    2011: "https://www.cdc.gov/yrbs/files/2011/yrbs2011.zip",
    2013: "https://www.cdc.gov/yrbs/files/2013/YRBS2013.zip",
    2015: "https://www.cdc.gov/yrbs/files/2015/yrbs2015.zip",
    2017: "https://www.cdc.gov/yrbs/files/2017/XXH2017_YRBS_Data.zip",
    2019: "https://www.cdc.gov/yrbs/files/2019/XXH2019_YRBS_Data.zip",
    2021: "https://www.cdc.gov/yrbs/files/2021/XXH2021_YRBS_Data.zip",
}

# SHA-256 de los .mdb finales (los que se extraen de cada .zip, NO el .zip).
# Tomados de references/data_provenance.md.
YRBS_SHA256 = {
    2005: "efe195059a396f11655446242d676a00eddc1ffe667329d8abae2b1183c5cad9",
    2007: "2fefb8e23df170ea8e6b49a2dea3e01341345a4b3207e16accd34b2f196ec441",
    2009: "cc3b358db3e962aab96847c13656d187a297ccda42868daed3f115560ccb41fb",
    2011: "e66538f4a05dfcc985b5c7f52cecb7b1de9f926cfbb7ab3e602e2c0e027bdbb3",
    2013: "1ac5da17ce1b94ba2b46826ee82bbe7a45d29b978e772ad1b32773d5d6e8128a",
    2015: "28088e68ec6ac9ed8123d50c2055fcfe39d65babf8ac6d6facda49928e4fcbf8",
    2017: "e28c6b56174e0bb8d37bec96afcc43dc819f35f8aea9b7ab4064e79defb37c4c",
    2019: "beae213846795bd6cc8961d1517243ac9a11384239ed00a0e6f909641c7ced65",
    2021: "8ed22a313eeec272998d76e45d5b4c1b4f375809db5a2b5ef97b8936dbb37645",
}

SOCRATA_URL = "https://data.cdc.gov/resource/w26f-tf3h.json"


def _http_get(url: str, dest: Path, *, chunk: int = 1 << 20, timeout: int = 120) -> None:
    """Descarga `url` a `dest` con barra de progreso simple."""
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        written = 0
        with dest.open("wb") as f:
            for chunk_bytes in r.iter_content(chunk_size=chunk):
                f.write(chunk_bytes)
                written += len(chunk_bytes)
        if total and written != total:
            raise IOError(
                f"Descarga incompleta de {url}: {written}/{total} bytes."
            )


def download_yrbs_year(year: int, *, force: bool = False) -> Path:
    """Descarga, descomprime y verifica el SHA-256 del .mdb de un año YRBS.

    Returns la ruta al .mdb final.
    """
    raw_dir = config.RAW_DIR / "yrbs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    mdb_path = raw_dir / f"yrbs{year}.mdb"

    if mdb_path.exists() and not force:
        actual = sha256_of(mdb_path)
        expected = YRBS_SHA256[year]
        if actual == expected:
            print(f"  [skip] yrbs{year}.mdb ya presente y verificado ({actual[:12]}…)")
            return mdb_path
        else:
            print(
                f"  [WARN] yrbs{year}.mdb presente pero SHA-256 no coincide "
                f"({actual[:12]}… vs {expected[:12]}…). Re-descargando."
            )
            mdb_path.unlink()

    url = YRBS_URLS[year]
    zip_path = raw_dir / f"yrbs{year}.zip"
    print(f"  [GET ] {url}")
    _http_get(url, zip_path)
    print(f"  [OK  ] {zip_path.name} ({zip_path.stat().st_size / 1e6:.1f} MB)")

    # Extraer solo el .mdb
    with zipfile.ZipFile(zip_path) as zf:
        mdb_members = [n for n in zf.namelist() if n.lower().endswith(".mdb")]
        if not mdb_members:
            raise IOError(f"No se encontró .mdb dentro de {zip_path}")
        # Si hay múltiples .mdb, tomar el primero
        member = mdb_members[0]
        with zf.open(member) as src, mdb_path.open("wb") as dst:
            dst.write(src.read())
    zip_path.unlink()  # Limpiar el zip
    print(f"  [OK  ] extraído a {mdb_path.name} ({mdb_path.stat().st_size / 1e6:.1f} MB)")

    # Verificar SHA-256
    actual = sha256_of(mdb_path)
    expected = YRBS_SHA256[year]
    if actual != expected:
        mdb_path.unlink()
        raise IOError(
            f"SHA-256 mismatch para yrbs{year}.mdb:\n"
            f"  esperado: {expected}\n"
            f"  obtenido: {actual}\n"
            f"Posible causa: el CDC actualizó el archivo. Actualice YRBS_SHA256."
        )
    print(f"  [✓   ] SHA-256 verificado ({actual[:12]}…)")
    return mdb_path


def download_socrata(*, force: bool = False) -> Path:
    """Descarga la mortalidad adolescente del Socrata de NCHS.

    Returns la ruta al CSV limpio.
    """
    out_dir = config.PROCESSED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "wonder_suicide_adolescent_2018_2024.csv"

    if out_path.exists() and not force:
        print(f"  [skip] {out_path.name} ya presente")
        return out_path

    import pandas as pd

    params = {
        "$where": "topic='Suicides' AND `group`='Sex and age group'",
        "$limit": 5000,
    }
    print(f"  [GET ] {SOCRATA_URL}")
    r = requests.get(SOCRATA_URL, params=params, timeout=120)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    # Filtrar a crude rate (no age-adjusted)
    df = df[df["estimate_type"].str.contains("crude", case=False, na=False)].copy()
    df = df[df["subgroup"].str.contains(r"10-14|15-19", na=False)].copy()
    df = df.rename(
        columns={
            "time_period": "year",
            "subgroup": "sex_age",
            "nesting_label": "sex",
            "estimate": "rate_per_100k",
            "standard_error": "se",
            "estimate_lci": "lci",
            "estimate_uci": "uci",
        }
    )
    df["year"] = df["year"].astype(int)
    for c in ["rate_per_100k", "se", "lci", "uci"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    out = df[
        ["year", "sex_age", "sex", "rate_per_100k", "se", "lci", "uci", "estimate_type"]
    ]
    out.to_csv(out_path, index=False)
    print(f"  [OK  ] {out_path.name}: {len(out)} filas")
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Descarga datos crudos de YRBS y NCHS Socrata."
    )
    parser.add_argument(
        "--year",
        type=int,
        choices=list(YRBS_URLS.keys()),
        help="Si se especifica, descarga solo ese año YRBS (default: los 9).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-descargar incluso si el archivo ya existe y está verificado.",
    )
    parser.add_argument(
        "--socrata-only",
        action="store_true",
        help="Solo descarga NCHS Socrata, no YRBS.",
    )
    parser.add_argument(
        "--yrbs-only",
        action="store_true",
        help="Solo descarga YRBS, no NCHS Socrata.",
    )
    args = parser.parse_args(argv)

    rc = 0
    if not args.socrata_only:
        years = [args.year] if args.year else list(YRBS_URLS.keys())
        print(f"=== Descargando YRBS ({len(years)} año(s)) ===")
        for y in years:
            try:
                download_yrbs_year(y, force=args.force)
            except Exception as e:
                print(f"  [FAIL] yrbs{y}: {e}", file=sys.stderr)
                rc = 1
    if not args.yrbs_only:
        print("=== Descargando NCHS Socrata (wonder_suicide_adolescent) ===")
        try:
            download_socrata(force=args.force)
        except Exception as e:
            print(f"  [FAIL] socrata: {e}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
