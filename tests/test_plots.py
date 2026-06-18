"""Tests para las utilidades de visualización."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # backend no-interactivo para tests

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from wired_apart import config
from wired_apart.plots import (
    _format_cell,
    apply_project_style,
    highlight_period,
    save,
    simpson_heatmap,
)


def test_apply_project_style_runs() -> None:
    """apply_project_style() no debe lanzar excepciones."""
    apply_project_style()
    # Verificar que el estilo se aplicó
    import matplotlib.pyplot as plt

    assert plt.rcParams["figure.dpi"] == config.FIGURE_DPI


def test_save_creates_file(tmp_path: Path) -> None:
    """save() crea el archivo en la ruta correcta."""
    apply_project_style()
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])

    # Usar un nombre (no Path) → va a FIGURES_DIR
    name = "test_fig_dummy"
    out = save(fig, name, fmt="png")
    assert out.exists()
    assert out.suffix == ".png"
    assert out.name == f"{name}.png"
    assert out.parent == config.FIGURES_DIR

    # Limpiar
    out.unlink()
    plt.close(fig)


def test_highlight_period_adds_patch() -> None:
    """highlight_period() añade un axvspan al eje."""
    apply_project_style()
    fig, ax = plt.subplots()
    ax.plot([2005, 2021], [0, 1])

    n_patches_before = len(ax.patches)
    highlight_period(ax)
    # axvspan añade patches
    assert len(ax.patches) > n_patches_before

    plt.close(fig)


def test_highlight_period_with_custom_range() -> None:
    """highlight_period() acepta start/end explícitos."""
    apply_project_style()
    fig, ax = plt.subplots()
    ax.plot([2000, 2025], [0, 1])

    highlight_period(ax, start=2010, end=2015, label="Test Rewiring", color="red")

    # Verificar que el label aparece en la legenda
    handles, labels = ax.get_legend_handles_labels()
    assert "Test Rewiring" in labels

    plt.close(fig)


# ---------------------------------------------------------------------------
# Simpson heatmap
# ---------------------------------------------------------------------------


def _toy_simpson_df() -> pd.DataFrame:
    """DataFrame mínimo para testar simpson_heatmap()."""
    rows = []
    for sex in ["Female", "Male"]:
        for race in ["White", "Black", "Hispanic", "Asian"]:
            rows.append(
                {
                    "sex": sex,
                    "race": race,
                    "delta_pp": 10.0,
                    "ci_lo": 5.0,
                    "ci_hi": 15.0,
                    "n_pre": 500,
                }
            )
    # Una celda con n_pre < 200 (NHPI) para verificar el asterisco
    for sex in ["Female", "Male"]:
        rows.append(
            {
                "sex": sex,
                "race": "NHPI",
                "delta_pp": -1.0,
                "ci_lo": -15.0,
                "ci_hi": 15.0,
                "n_pre": 128,
            }
        )
    return pd.DataFrame(rows)


def test_format_cell_two_lines_and_asterisk() -> None:
    """_format_cell devuelve 2 líneas; '*' solo si small_n=True."""
    out_small = _format_cell(13.0, -3.6, 26.9, small_n=True)
    out_big = _format_cell(13.0, -3.6, 26.9, small_n=False)
    assert "\n" in out_small
    assert out_small.startswith("+13.0*")
    assert "[-3.6,+26.9]" in out_small
    assert "*" not in out_big
    assert out_big.startswith("+13.0")


def test_simpson_heatmap_renders(tmp_path: Path) -> None:
    """simpson_heatmap() produce una figura sin errores y la guarda."""
    apply_project_style()
    fig = simpson_heatmap(_toy_simpson_df(), save_name=None)
    assert fig is not None
    # rcParams restaurados al salir (no debe filtrar el context "paper")
    assert plt.rcParams["font.size"] > 14  # talk context sigue activo
    plt.close(fig)


def test_simpson_heatmap_uses_paper_context(tmp_path: Path) -> None:
    """Dentro de simpson_heatmap, las anotaciones no están a 18pt.

    Reproduce el bug original: con ``context='talk'``, ``annot_kws``
    se ignora y el texto se renderiza a ~18pt. La función debe
    forzar un tamaño explícito sobre los Text del heatmap.
    """
    apply_project_style()
    fig, ax = plt.subplots()
    simpson_heatmap(_toy_simpson_df(), ax=ax, save_name=None)
    # Buscar los Text de anotación (los puso sns.heatmap)
    annot_texts = [t for t in ax.texts if t.get_text() and "\n" in t.get_text()]
    assert annot_texts, "No se encontraron anotaciones de 2 líneas"
    sizes = {round(t.get_fontsize(), 1) for t in annot_texts}
    # Si el bug reaparece, todos los textos tendrán ~16-18pt.
    # Con la corrección deben estar alrededor del annot_fontsize (9pt)
    # o explícitamente <= 12pt.
    assert all(s <= 12 for s in sizes), (
        f"anotaciones demasiado grandes (talk context no aislado): {sizes}"
    )
    plt.close(fig)


def test_simpson_heatmap_annotates_small_n() -> None:
    """Las celdas con n_pre < small_n_threshold llevan asterisco."""
    apply_project_style()
    fig, ax = plt.subplots()
    simpson_heatmap(_toy_simpson_df(), small_n_threshold=200, ax=ax, save_name=None)
    # NHPI (n_pre=128) debe llevar '*' en la primera línea del text.
    # Verificamos que la celda de NHPI (delta = -1.0) tenga '*\n' en
    # su string, mientras que las celdas grandes (delta = 10.0) NO.
    text_values = [t.get_text() for t in ax.texts]
    nhpi_with_star = [t for t in text_values if t.startswith("-1.0*")]
    big_without_star = [t for t in text_values if t.startswith("+10.0")]
    assert nhpi_with_star, f"NHPI no tiene '*': {sorted(set(text_values))[:6]}"
    assert big_without_star, (
        f"Celdas grandes (n_pre=500) perdieron su formato: {sorted(set(text_values))[:6]}"
    )
    assert all("*\n" not in t for t in big_without_star), (
        "Una celda grande (n_pre=500) tiene '*' — umbral mal aplicado"
    )
    plt.close(fig)


def test_simpson_heatmap_raises_on_missing_columns() -> None:
    """simp_df sin columnas requeridas → ValueError explícito."""
    apply_project_style()
    bad = pd.DataFrame({"sex": ["F"], "race": ["White"], "delta_pp": [1.0]})
    with pytest.raises(ValueError, match="faltan"):
        simpson_heatmap(bad, save_name=None)


def test_simpson_heatmap_raises_on_empty() -> None:
    """simp_df sin filas → ValueError explícito (no silencioso)."""
    apply_project_style()
    cols = ["sex", "race", "delta_pp", "ci_lo", "ci_hi", "n_pre"]
    with pytest.raises(ValueError, match="vacío"):
        simpson_heatmap(pd.DataFrame(columns=cols), save_name=None)
