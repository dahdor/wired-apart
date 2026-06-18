"""Utilidades de visualización con la paleta consistente del proyecto."""

from __future__ import annotations

from collections.abc import Iterator
import contextlib
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from wired_apart import config


def apply_project_style() -> None:
    """Aplica la paleta y estilo consistente en todas las figuras."""
    sns.set_theme(
        style="whitegrid",
        context="talk",
        palette=list(config.COLOR_PALETTE.values()),
    )
    plt.rcParams.update(
        {
            "figure.dpi": config.FIGURE_DPI,
            "savefig.dpi": config.FIGURE_DPI,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.family": "DejaVu Sans",
        }
    )


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


def highlight_period(
    ax,
    start: int | None = None,
    end: int | None = None,
    label: str = "Great Rewiring",
    color: str | None = None,
    alpha: float = 0.15,
) -> None:
    """Sombrea la ventana del Great Rewiring (2010-2015) en un eje de tiempo.

    Los defaults se leen de `config.REWIRING_START_YEAR` y `REWIRING_END_YEAR`
    para que la narrativa sea consistente entre todas las figuras.
    """
    start = start if start is not None else config.REWIRING_START_YEAR
    end = end if end is not None else config.REWIRING_END_YEAR
    color = color or config.COLOR_PALETTE["secondary"]
    ax.axvspan(start, end, alpha=alpha, color=color, label=label, zorder=0)


@contextlib.contextmanager
def _paper_context(font_scale: float = 1.0) -> Iterator[None]:
    """Context manager que fuerza un tamaño de letra "paper" temporalmente.

    El estilo del proyecto usa ``context="talk"`` (letras grandes) que
    es ideal para figuras de tendencia, pero **invalida** el parámetro
    ``annot_kws={"fontsize": ...}`` de ``sns.heatmap``: las anotaciones
    terminan renderizadas a 16-18pt y desbordan las celdas. Para
    heatmaps con anotaciones largas (CI95, n pequeño) necesitamos
    un contexto "notebook" con ``font_scale`` explícito.

    Restaura los ``rcParams`` previos al salir, así que es seguro de
    usar dentro de un cuaderno sin afectar a figuras posteriores.
    """
    rc_backup = mpl.rcParams.copy()
    try:
        sns.set_context("notebook", font_scale=font_scale)
        # Reaplicar overrides del proyecto que `set_context` pisa
        mpl.rcParams.update(
            {
                "font.family": "DejaVu Sans",
                "figure.dpi": config.FIGURE_DPI,
                "savefig.dpi": config.FIGURE_DPI,
            }
        )
        yield
    finally:
        mpl.rcParams.update(rc_backup)


def _format_cell(delta: float, lo: float, hi: float, *, small_n: bool) -> str:
    """Formato de anotación de una celda del heatmap Simpson.

    Devuelve un string de DOS líneas:

        +X.X*           ← delta_pp con signo y asterisco si n_pre<200
        [-Y.Y,+Z.Z]     ← IC95 bootstrap

    El salto de línea es lo que evita que las celdas se vean "bloat":
    con ``talk`` context una sola línea ancha se sale del cuadrado;
    con dos líneas el ancho de cada una cabe en la celda incluso a
    8.5" de ancho.
    """
    star = "*" if small_n else ""
    return f"{delta:+.1f}{star}\n[{lo:+.1f},{hi:+.1f}]"


def simpson_heatmap(
    simp_df: pd.DataFrame,
    *,
    small_n_threshold: int = 200,
    title: str | None = None,
    subtitle: str | None = None,
    figsize: tuple[float, float] = (8.5, 6.0),
    cmap: str = "RdBu_r",
    cbar_label: str = "Δ sad/hopeless (pp)",
    save_name: str | None = "fig11_simpson_heatmap",
    ax: plt.Axes | None = None,
    annot_fontsize: float = 9.0,
) -> plt.Figure:
    """Heatmap de la Paradoja de Simpson con anotaciones legibles.

    Muestra el cambio pre(2007-2009) → post(2017-2021) en
    ``sad_hopeless`` (en puntos porcentuales) estratificado por
    ``sex × race`` (CDC ``raceeth``, 8 categorías). Cada celda lleva
    el delta y el IC95 bootstrap apilados en dos líneas, con un
    asterisco marcando las celdas con ``n_pre < small_n_threshold``
    (estimación ruidosa, IC95 ancho).

    Parameters
    ----------
    simp_df : DataFrame
        Formato largo con una fila por ``(sex, race)``. Columnas
        requeridas: ``sex``, ``race``, ``delta_pp``, ``ci_lo``,
        ``ci_hi``, ``n_pre``. ``n_pre < small_n_threshold`` activa
        la marca de "estimación ruidosa".
    small_n_threshold : int, default 200
        Umbral de n para marcar con ``*`` (alineado con la §5.6 del
        informe).
    title, subtitle : str, optional
        Líneas de título. Si ambos son None se usa un título por
        defecto alineado con la narrativa del informe.
    figsize : tuple, default ``(8.5, 6.0)``
        Tamaño de la figura en pulgadas. Pensado para encajar en
        un layout de dos columnas de LaTeX/Quarto.
    cmap : str, default ``"RdBu_r"``
        Colormap divergente (centrada en 0).
    cbar_label : str
        Etiqueta de la colorbar.
    save_name : str, optional
        Si se da, guarda la figura en
        ``config.FIGURES_DIR / f"{save_name}.{config.FIGURE_FORMAT}"``.
    ax : matplotlib Axes, optional
        Si se da, dibuja sobre estos ejes. Si no, crea una figura
        nueva.
    annot_fontsize : float, default 9.0
        Tamaño (pt) de las anotaciones dentro de las celdas. Se
        aplica con un contexto "notebook" temporal, así que NO se
        ve afectado por ``context="talk"`` del proyecto.

    Returns
    -------
    matplotlib.figure.Figure

    Notes
    -----
    El diseño prioriza legibilidad de la información cuantitativa
    completa (delta + IC95) por celda, en vez de solo el color. La
    estrella ``*`` alerta sobre celdas con ``n_pre < 200`` y debe
    interpretarse siempre en conjunto con el IC95 — un IC95 que
    cruza 0 puede deberse a ruido muestreal, no a estabilidad.
    """
    required = {"sex", "race", "delta_pp", "ci_lo", "ci_hi", "n_pre"}
    missing = required - set(simp_df.columns)
    if missing:
        raise ValueError(
            f"simp_df debe tener columnas {sorted(required)}, faltan: {sorted(missing)}"
        )
    if simp_df.empty:
        raise ValueError("simp_df está vacío; no hay nada que graficar.")

    pivot_delta = simp_df.pivot_table(values="delta_pp", index="race", columns="sex")
    pivot_ci_lo = simp_df.pivot_table(values="ci_lo", index="race", columns="sex")
    pivot_ci_hi = simp_df.pivot_table(values="ci_hi", index="race", columns="sex")
    pivot_n = simp_df.pivot_table(values="n_pre", index="race", columns="sex")

    # Construir la matriz de anotaciones (string de 2 líneas por celda)
    annot = pivot_delta.copy().astype(object)
    for r in annot.index:
        for s in annot.columns:
            d = pivot_delta.loc[r, s]
            lo = pivot_ci_lo.loc[r, s]
            hi = pivot_ci_hi.loc[r, s]
            n = pivot_n.loc[r, s]
            if pd.isna(d) or pd.isna(lo) or pd.isna(hi):
                annot.loc[r, s] = ""
                continue
            small_n = bool(pd.notna(n) and n < small_n_threshold)
            annot.loc[r, s] = _format_cell(d, lo, hi, small_n=small_n)

    # Rango simétrico del colormap alrededor de 0 (mismo para todas
    # las corridas → comparabilidad entre revisiones)
    vmax = float(np.nan_to_num(pivot_delta.values, nan=0).max())
    vmin = float(np.nan_to_num(pivot_delta.values, nan=0).min())
    vlim = max(abs(vmax), abs(vmin), 1.0)  # ≥1pp para que el cmap no colapse

    if title is None:
        title = (
            "Cambio en sad/hopeless (pre 2007-09 → post 2017-21)\n"
            "por sexo × raza — YRBS, ponderado"
        )
    if subtitle is None:
        subtitle = (
            f"Celdas: Δpp  [IC95 bootstrap].  * = n_pre < {small_n_threshold} (estimación ruidosa)"
        )

    # Componer título (título + subtítulo en el mismo Axes; no en un
    # `ax.text` flotante, para que `bbox="tight"` no se lo lleve por
    # delante en distintas versiones de matplotlib).
    full_title = f"{title}\n{subtitle}"

    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    with _paper_context(font_scale=1.0):
        sns.heatmap(
            pivot_delta,
            annot=annot,
            fmt="",
            cmap=cmap,
            center=0,
            vmin=-vlim,
            vmax=vlim,
            linewidths=0.5,
            linecolor="white",
            cbar_kws={"label": cbar_label, "shrink": 0.85},
            ax=ax,
            annot_kws={
                "fontsize": annot_fontsize,
                "fontfamily": "DejaVu Sans",
                "linespacing": 1.15,
            },
        )

    ax.set_title(full_title, fontsize=12, pad=14, loc="left")
    ax.set_xlabel("Sexo", fontsize=11)
    ax.set_ylabel("Raza (CDC raceeth)", fontsize=11)
    ax.tick_params(axis="both", labelsize=10)

    # Ticks centrados en la celda (default de heatmap, pero por si
    # una versión futura de seaborn lo cambia)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha="center")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    if own_fig:
        # subplots_adjust deja sitio para el título de 2 líneas; usar
        # `tight_layout` recorta el renglón superior en matplotlib ≥3.8
        # cuando hay titles largos. `right=0.93` deja espacio para la
        # colorbar con su label.
        fig.subplots_adjust(top=0.82, left=0.18, right=0.92, bottom=0.12)

    if save_name is not None and own_fig:
        save(fig, save_name)

    return fig
