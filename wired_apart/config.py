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
# Monitoring the Future (MTF) — University of Michigan / NIDA
# Series 1975+, adolescents 8th, 10th, 12th grade.
# Public download: https://monitoringthefuture.org/data-data
MTF_URL = "https://monitoringthefuture.org/data-data"
MTF_DATA_DICT = REFERENCES_DIR / "mtf_data_dictionary.md"

# National Survey on Drug Use and Health (NSDUH) — SAMHSA
# Annual cross-sectional, ages 12+, with adolescent mental-health modules.
# Public download: https://www.samhsa.gov/data/data-we-collect/nsduh
NSDUH_URL = "https://www.samhsa.gov/data/data-we-collect/nsduh"
NSDUH_DATA_DICT = REFERENCES_DIR / "nsduh_data_dictionary.md"

# --- Time window for the analysis --------------------------------------------
# The book dates "The Great Rewiring" to 2010-2015. We want 5 years of "before"
# and 5 years of "after" that window, plus the post-COVID inflection in 2020.
ANALYSIS_START_YEAR = 2005
ANALYSIS_END_YEAR = 2020

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
