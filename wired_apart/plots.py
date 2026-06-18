"""Utilidades de visualización con la paleta consistente del proyecto."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from wired_apart import config


def apply_project_style() -> None:
    """Aplica la paleta y estilo consistente en todas las figuras."""
    sns.set_theme(
        style="whitegrid",
        context="talk",
        palette=list(config.COLOR_PALETTE.values()),
    )
    plt.rcParams.update({
        "figure.dpi": config.FIGURE_DPI,
        "savefig.dpi": config.FIGURE_DPI,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.family": "DejaVu Sans",
    })


def save(fig, name: str, fmt: str | None = None) -> Path:
    """Guarda una figura en `reports/figures/` con el formato configurado."""
    if isinstance(name, Path):
        out = name
    else:
        fmt = fmt or config.FIGURE_FORMAT
        out = config.FIGURES_DIR / f"{name}.{fmt}"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=fmt)
    return out


def highlight_period(ax, start: int | None = None, end: int | None = None,
                    label: str = "Great Rewiring",
                    color: str | None = None, alpha: float = 0.15) -> None:
    """Sombrea la ventana del Great Rewiring (2010-2015) en un eje de tiempo.

    Los defaults se leen de `config.REWIRING_START_YEAR` y `REWIRING_END_YEAR`
    para que la narrativa sea consistente entre todas las figuras.
    """
    start = start if start is not None else config.REWIRING_START_YEAR
    end = end if end is not None else config.REWIRING_END_YEAR
    color = color or config.COLOR_PALETTE["secondary"]
    ax.axvspan(start, end, alpha=alpha, color=color,
               label=label, zorder=0)
