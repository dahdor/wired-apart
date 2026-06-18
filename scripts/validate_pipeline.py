"""Validación end-to-end del pipeline.

Ejecuta el pipeline completo (download → notebooks → report) y verifica que
los outputs clave existen y pasan tests estadísticos. Diseñado para correr
en CI (GitHub Actions) y para auditoría manual.

Uso:
    uv run python scripts/validate_pipeline.py            # todo
    uv run python scripts/validate_pipeline.py --skip-download  # si los datos ya están
    uv run python scripts/validate_pipeline.py --skip-render    # solo pipeline, sin report
    uv run python scripts/validate_pipeline.py --skip-pdf       # solo HTML, saltea PDF + TinyTeX
    uv run python scripts/validate_pipeline.py --install-tinytex  # fuerza TinyTeX aunque haya LaTeX
    uv run python scripts/validate_pipeline.py --quick         # solo tests + verificación outputs

Exit code 0 = todo OK, 1 = algún paso falló.

Notas sobre LaTeX (PDF):
- Si el sistema tiene lualatex/xelatex/pdflatex (MiKTeX en Windows, TeX
  Live en Linux), el script lo detecta y NO descarga TinyTeX. Es la ruta
  rápida: 0-1 min extra para el PDF.
- Si no hay motor LaTeX, se instala TinyTeX (~1 GB, 10-30 min). La
  instalación se muestra con progreso (no usamos --quiet).
- Con --skip-pdf, ni se detecta ni se instala nada de LaTeX.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from wired_apart import config, force_utf8_stdout

# Reconfigurar stdout/stderr a UTF-8 para que caracteres como í, ñ,
# á, ó se impriman correctamente en Windows. Ver
# wired_apart.force_utf8_stdout para detalles.
force_utf8_stdout()

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


# Orden de preferencia de motores LaTeX. Quarto los auto-detecta; nosotros
# solo necesitamos saber si hay ALGUNO disponible para saltarnos la
# descarga de TinyTeX (varios GB). `lualatex` primero porque es el engine
# por defecto en Quarto >= 1.4 y el que usa el script cuando se invoca
# en laptops con MiKTeX/Tex Live preinstalado.
LATEX_ENGINE_PREFERENCE = ("lualatex", "xelatex", "pdflatex")


def find_latex_engine() -> str | None:
    """Devuelve el primer motor LaTeX disponible en PATH, o None.

    Se usa para decidir si hace falta instalar TinyTeX: si el sistema ya
    tiene un motor LaTeX (MiKTeX en Windows, TeX Live en Linux/macOS),
    Quarto lo usará directamente y no necesitamos la descarga de
    varios GB de TinyTeX.
    """
    for engine in LATEX_ENGINE_PREFERENCE:
        if shutil.which(engine) is not None:
            return engine
    return None


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
    parser.add_argument(
        "--skip-download", action="store_true", help="Saltar descarga de datos crudos."
    )
    parser.add_argument(
        "--skip-render", action="store_true", help="Saltar renderizado del informe Quarto."
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Saltar SOLO el render PDF (HTML sí se genera). "
        "Implica saltarse la instalación de TinyTeX. "
        "Útil cuando no hay LaTeX en el sistema o no se "
        "quiere esperar la descarga (~1 GB).",
    )
    parser.add_argument(
        "--install-tinytex",
        action="store_true",
        help="Fuerza la instalación de TinyTeX aunque haya "
        "un motor LaTeX en el sistema. Útil para CI "
        "donde se quiere pinchar la versión de LaTeX.",
    )
    parser.add_argument(
        "--quick", action="store_true", help="Solo correr tests + verificar outputs."
    )
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
    steps_ok.append(step("pytest (validación inicial)", py_prefix + ["pytest", "tests/", "-v"]))
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
            print("  Razón: requiere Microsoft Access ODBC driver (Windows-only).")
            print("  El output (data/processed/yrbs_2005_2021.parquet) ya está commiteado.")
            continue
        steps_ok.append(
            step(
                f"notebook {label} ({Path(path).stem})",
                py_prefix
                + ["jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", path],
            )
        )
    # Re-correr tests después del pipeline (detecta drift)
    steps_ok.append(step("pytest (post-pipeline)", py_prefix + ["pytest", "tests/", "-v"]))
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
        # Decidir motor LaTeX para el PDF. Si el sistema ya tiene uno
        # (MiKTeX en Windows, TeX Live en Linux/macOS) NO instalamos
        # TinyTeX — su distribución son varios GB y la descarga puede
        # tardar 10-30 min incluso con buena conexión, sin progreso
        # visible porque quarto install tinytex --quiet silencia la
        # salida. Solo instalamos TinyTeX si (a) no hay motor en sistema
        # Y (b) el usuario no pasó --skip-pdf.
        if shutil.which("quarto") is not None:
            latex_engine = find_latex_engine()
            if args.skip_pdf:
                print("\n=== PDF render SKIPPED (--skip-pdf) ===")
                print("  No se instala TinyTeX; solo se genera el HTML.")
            elif latex_engine is not None and not args.install_tinytex:
                print(f"\n=== LaTeX: usando {latex_engine} del sistema ===")
                print("  TinyTeX NO se instala (ahorramos ~1 GB de descarga).")
                print("  Para forzar TinyTeX, usá --install-tinytex.")
            else:
                if latex_engine is None:
                    print("\n=== LaTeX: no se detectó motor en sistema ===")
                    print("  Motores buscados: " + ", ".join(LATEX_ENGINE_PREFERENCE))
                    print("  Se instalará TinyTeX (puede tardar varios minutos).")
                else:
                    print("\n=== LaTeX: forzando TinyTeX (--install-tinytex) ===")
                    print(f"  Motor del sistema ignorado: {latex_engine}")
                # Sin --quiet: el usuario debe ver el progreso de descarga.
                steps_ok.append(step("quarto install tinytex", ["quarto", "install", "tinytex"]))
        steps_ok.append(
            step(
                "quarto render html",
                [
                    "quarto",
                    "render",
                    "informe.qmd",
                    "--to",
                    "html",
                    "--output-dir",
                    "reports",
                    "--no-cache",
                ],
            )
        )
        if not args.skip_pdf:
            steps_ok.append(
                step(
                    "quarto render pdf",
                    [
                        "quarto",
                        "render",
                        "informe.qmd",
                        "--to",
                        "pdf",
                        "--output-dir",
                        "reports",
                        "--no-cache",
                    ],
                )
            )
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
