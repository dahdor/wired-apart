"""Tests para las utilidades de visualización."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # backend no-interactivo para tests

from pathlib import Path
import matplotlib.pyplot as plt

from wired_apart import config
from wired_apart.plots import apply_project_style, save, highlight_period


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
