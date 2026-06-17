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
    fmt = fmt or config.FIGURE_FORMAT
    out = config.FIGURES_DIR / f"{name}.{fmt}"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, format=fmt)
    return out


def highlight_period(ax, start: int = 2010, end: int = 2015, label: str = "Great Rewiring") -> None:
    """Sombrea la ventana 2010-2015 en un eje de tiempo para anclar la narrativa."""
    ax.axvspan(start, end, alpha=0.15, color=config.COLOR_PALETTE["secondary"],
               label=label, zorder=0)
