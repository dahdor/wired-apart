"""Validación end-to-end del pipeline.

Ejecuta el pipeline completo (download → notebooks → report) y verifica que
los outputs clave existen y pasan tests estadísticos. Diseñado para correr
en CI (GitHub Actions) y para auditoría manual.

Uso:
    uv run python scripts/validate_pipeline.py            # todo
    uv run python scripts/validate_pipeline.py --skip-download  # si los datos ya están
    uv run python scripts/validate_pipeline.py --skip-render    # solo pipeline, sin report
    uv run python scripts/validate_pipeline.py --quick         # solo tests + verificación outputs

Exit code 0 = todo OK, 1 = algún paso falló.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from wired_apart import config

# El notebook 0.0 usa pyodbc + Microsoft Access Driver, que solo está
# disponible en Windows. En Linux/macOS, los .mdb no se pueden convertir,
# pero `data/processed/yrbs_2005_2021.parquet` ya viene commiteado al repo
# (es la salida del notebook 0.0) y los notebooks 1.0-5.0 funcionan
# sin ODBC.
SKIP_NOTEBOOKS_ON_LINUX = {"0.0-dh-data-acquisition.ipynb"}


def _py() -> str:
    """Devuelve el ejecutable de Python que debe usarse para subprocesos.

    Si `uv` está disponible, prefiere `uv run python` (usa el .venv del
    proyecto, donde están las dependencias). Si no, cae al Python que
    ejecuta este script.
    """
    if shutil.which("uv"):
        return "uv"
    return sys.executable


def step(name: str, cmd: list[str], *, cwd: Path | None = None) -> bool:
    """Ejecuta `cmd`, imprime output, retorna True si exit 0."""
    print(f"\n=== {name} ===")
    print(f"  $ {' '.join(cmd)}")
    rc = subprocess.call(cmd, cwd=cwd or PROJECT_ROOT)
    if rc != 0:
        print(f"  [FAIL] {name} (exit {rc})", file=sys.stderr)
    return rc == 0


def check_outputs() -> list[str]:
    """Verifica que los outputs clave existen y son no-vacíos."""
    issues: list[str] = []
    expected = [
        config.PROCESSED_DIR / "yrbs_2005_2021.parquet",
        config.PROCESSED_DIR / "yrbs_clean_2005_2021.parquet",
        config.PROCESSED_DIR / "wonder_suicide_adolescent_2018_2024.csv",
        config.PROCESSED_DIR / "wonder_clean_2005_2024.csv",
        config.REPORTS_DIR / "informe.html",
        config.REPORTS_DIR / "informe.pdf",
    ]
    for path in expected:
        if not path.exists():
            issues.append(f"FALTA: {path}")
        elif path.stat().st_size == 0:
            issues.append(f"VACÍO: {path}")
        else:
            size = path.stat().st_size
            unit = "B"
            for u in ["KB", "MB"]:
                if size > 1024:
                    size /= 1024
                    unit = u
            print(f"  [OK] {path.relative_to(PROJECT_ROOT)} ({size:.1f} {unit})")
    # Verificar que hay figuras
    figs = list(config.FIGURES_DIR.glob("*.png"))
    if len(figs) < 10:
        issues.append(f"Solo {len(figs)} figuras en {config.FIGURES_DIR}, esperado ≥ 10")
    else:
        print(f"  [OK] {len(figs)} figuras en {config.FIGURES_DIR}")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validación end-to-end.")
    parser.add_argument("--skip-download", action="store_true",
                        help="Saltar descarga de datos crudos.")
    parser.add_argument("--skip-render", action="store_true",
                        help="Saltar renderizado del informe Quarto.")
    parser.add_argument("--quick", action="store_true",
                        help="Solo correr tests + verificar outputs.")
    args = parser.parse_args(argv)

    if args.quick:
        print("=== Modo quick: solo tests + outputs ===")
        py = _py()
        if py == "uv":
            ok = step("pytest", ["uv", "run", "pytest", "tests/", "-v"])
        else:
            ok = step("pytest", [py, "-m", "pytest", "tests/", "-v"])
        if not ok:
            return 1
        issues = check_outputs()
        if issues:
            print("\n[FALLO] Outputs faltantes:", file=sys.stderr)
            for i in issues:
                print(f"  - {i}", file=sys.stderr)
            return 1
        print("\n[OK] Todos los outputs presentes y tests pasaron.")
        return 0

    # Pipeline completo
    steps_ok: list[bool] = []
    py = _py()
    py_prefix = ["uv", "run"] if py == "uv" else [py, "-m"]

    if not args.skip_download:
        steps_ok.append(step("download_data", py_prefix + ["scripts/download_data.py"]))
    steps_ok.append(step("pytest (validación inicial)",
                          py_prefix + ["pytest", "tests/", "-v"]))
    # Notebooks en orden, saltando los platform-specific en Linux.
    is_windows = platform.system() == "Windows"
    notebooks = [
        ("0.0", "notebooks/0.0-dh-data-acquisition.ipynb"),
        ("1.0", "notebooks/1.0-dh-yrbs-cleaning.ipynb"),
        ("1.1", "notebooks/1.1-dh-wonder-cleaning.ipynb"),
        ("2.0", "notebooks/2.0-dh-eda-yrbs.ipynb"),
        ("2.1", "notebooks/2.1-dh-eda-wonder.ipynb"),
        ("3.0", "notebooks/3.0-dh-analysis.ipynb"),
        ("4.0", "notebooks/4.0-dh-storytelling.ipynb"),
        ("5.0", "notebooks/5.0-dh-solution.ipynb"),
    ]
    for label, path in notebooks:
        nb_name = Path(path).name
        if not is_windows and nb_name in SKIP_NOTEBOOKS_ON_LINUX:
            print(f"\n=== Saltando notebook {label} ({nb_name}) en {platform.system()} ===")
            print(f"  Razón: requiere Microsoft Access ODBC driver (Windows-only).")
            print(f"  El output (data/processed/yrbs_2005_2021.parquet) ya está commiteado.")
            continue
        steps_ok.append(step(
            f"notebook {label} ({Path(path).stem})",
            py_prefix + ["jupyter", "nbconvert", "--to", "notebook",
                          "--execute", "--inplace", path],
        ))
    # Re-correr tests después del pipeline (detecta drift)
    steps_ok.append(step("pytest (post-pipeline)",
                          py_prefix + ["pytest", "tests/", "-v"]))
    if not args.skip_render:
        # Asegurar que quarto está en el PATH; sin esto, subprocess.call()
        # no lo encuentra aunque esté en ~/.local/quarto/bin.
        if shutil.which("quarto") is None:
            local_quarto = Path.home() / ".local" / "quarto" / "bin"
            if (local_quarto / "quarto").exists():
                os.environ["PATH"] = f"{local_quarto}:{os.environ.get('PATH', '')}"
                print(f"  [info] Añadido {local_quarto} al PATH para esta corrida.")
            else:
                print(
                    "  [WARN] 'quarto' no está en PATH. Instálalo con:\n"
                    "         https://quarto.org/docs/get-started/\n"
                    "         y re-ejecuta 'make install' (que también instala TinyTeX).",
                    file=sys.stderr,
                )
        # TinyTeX (LaTeX) es necesario para el PDF. quarto's install tinytex
        # es idempotente: si ya está, no hace nada.
        if shutil.which("quarto") is not None:
            print("\n=== TinyTeX check (necesario para PDF) ===")
            steps_ok.append(step("quarto install tinytex",
                                 ["quarto", "install", "tinytex", "--quiet"]))
        steps_ok.append(step("quarto render html",
                              ["quarto", "render", "informe.qmd", "--to", "html",
                               "--output-dir", "reports", "--no-cache"]))
        steps_ok.append(step("quarto render pdf",
                              ["quarto", "render", "informe.qmd", "--to", "pdf",
                               "--output-dir", "reports", "--no-cache"]))
    # Verificación final
    issues = check_outputs()

    print("\n=== Resumen ===")
    print(f"  Pasos OK: {sum(steps_ok)}/{len(steps_ok)}")
    print(f"  Outputs con problemas: {len(issues)}")
    if not all(steps_ok) or issues:
        print("\n[FAIL] Validación con problemas.", file=sys.stderr)
        return 1
    print("\n[OK] Validación end-to-end exitosa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
