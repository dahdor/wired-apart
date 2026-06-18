"""Configuration and constants for the wired-apart project.

All paths are resolved relative to the project root so that the analysis is
reproducible from any working directory.
"""
from pathlib import Path

# Project root = parent of the package directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# --- Directory layout ---------------------------------------------------------
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXTERNAL_DIR = DATA_DIR / "external"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
REFERENCES_DIR = PROJECT_ROOT / "references"

# --- Data sources (publicly available, US) -----------------------------------
# CDC Youth Risk Behavior Surveillance System (YRBS) — National High School
# Series 1991-present, every odd year. Public download, Access/ASCII format.
# Contains BOTH exposure (screen time, Q80) and outcomes (sadness, suicide, Q25-28).
YRBS_URL = "https://www.cdc.gov/yrbs/data/index.html"
YRBS_DATA_DICT = REFERENCES_DIR / "yrbs_data_dictionary.md"

# CDC WONDER — Underlying Cause of Death (compressed mortality file, 1999-2020)
# Public query interface + API. Provides suicide rates by age/sex/year.
WONDER_URL = "https://wonder.cdc.gov/ucd-icd10.html"
WONDER_DATA_DICT = REFERENCES_DIR / "wonder_data_dictionary.md"

# --- Time window for the analysis --------------------------------------------
# YRBS surveys run every odd year (2005, 2007, ... 2021). We include 9 waves
# to cover 5 years before the Great Rewiring (2005-2009), the rewiring window
# itself (2010-2015), and the post-rewiring + COVID era (2017-2021).
ANALYSIS_START_YEAR = 2005
ANALYSIS_END_YEAR = 2021

# Great Rewiring window per Haidt (2024). Used by the
# `highlight_period` plot helper and the `assign_rewiring_period` feature.
REWIRING_START_YEAR = 2010
REWIRING_END_YEAR = 2015

# --- Output paths ------------------------------------------------------------
INFORME_QMD = PROJECT_ROOT / "informe.qmd"
QUARTO_YML = PROJECT_ROOT / "_quarto.yml"
LOGO_UNIMET = REPORTS_DIR / "logo-unimet.png"

# --- Plotting defaults --------------------------------------------------------
FIGURE_DPI = 300
FIGURE_FORMAT = "png"
COLOR_PALETTE = {
    "primary": "#1f3a5f",   # deep blue
    "secondary": "#c8462b", # signal red
    "accent":    "#7a9e7e", # sage
    "neutral":   "#bdbdbd", # grey
    "highlight": "#f4b400", # gold
}

# Reproducibility
RANDOM_SEED = 2026
