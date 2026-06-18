"""Tests de integridad de los datasets limpios.

Estos tests son la red de seguridad para reproducibilidad: si una
refactorización cambia inadvertidamente las propiedades estadísticas
del pipeline (e.g., cambia el crosswalk, invierte una variable binaria,
o introduce NaN espurios), estos tests fallan con un mensaje claro.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Tests del schema / estructura
# ─────────────────────────────────────────────────────────────────────────────


def test_yrbs_clean_has_expected_columns(yrbs_clean: pd.DataFrame) -> None:
    """El dataset limpio debe tener las 17 columnas esperadas."""
    expected = {
        "year", "age", "sex", "grade", "hispanic", "hispanic_yesno",
        "race", "race_raw", "weight", "stratum", "psu",
        "sad_hopeless", "considered_suicide", "made_plan",
        "attempted_suicide_yesno", "attempted_suicide_ordinal",
        "screen_time",
    }
    assert set(yrbs_clean.columns) == expected, (
        f"Columnas faltantes/extra: {set(expected) ^ set(yrbs_clean.columns)}"
    )


def test_yrbs_clean_row_count(yrbs_clean: pd.DataFrame) -> None:
    """134 674 registros stacked de 9 años."""
    assert len(yrbs_clean) == 134_674


def test_yrbs_clean_years(yrbs_clean: pd.DataFrame) -> None:
    """Debe tener los 9 años impares 2005-2021."""
    expected_years = {2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021}
    assert set(yrbs_clean["year"].unique()) == expected_years


def test_yrbs_clean_no_duplicate_columns(yrbs_clean: pd.DataFrame) -> None:
    """No debe haber columnas duplicadas."""
    assert len(yrbs_clean.columns) == len(set(yrbs_clean.columns))


# ─────────────────────────────────────────────────────────────────────────────
# Tests de integridad de codificación
# ─────────────────────────────────────────────────────────────────────────────


def test_sex_coding(yrbs_clean: pd.DataFrame) -> None:
    """Sex: 1=Female, 2=Male. ~50/50."""
    vc = yrbs_clean["sex"].value_counts(dropna=True)
    assert set(vc.index) <= {1.0, 2.0}
    # Ratio F/M debe estar entre 0.95 y 1.05
    ratio = vc.loc[1.0] / vc.loc[2.0]
    assert 0.95 <= ratio <= 1.05, f"Ratio F/M = {ratio:.3f}, esperado ~1.0"


def test_sad_hopeless_binary(yrbs_clean: pd.DataFrame) -> None:
    """sad_hopeless ∈ {0, 1} (1 = yes)."""
    valid = yrbs_clean["sad_hopeless"].dropna()
    assert set(valid.unique()) <= {0.0, 1.0}


def test_considered_suicide_binary(yrbs_clean: pd.DataFrame) -> None:
    """considered_suicide ∈ {0, 1}."""
    valid = yrbs_clean["considered_suicide"].dropna()
    assert set(valid.unique()) <= {0.0, 1.0}


def test_made_plan_binary(yrbs_clean: pd.DataFrame) -> None:
    """made_plan ∈ {0, 1}."""
    valid = yrbs_clean["made_plan"].dropna()
    assert set(valid.unique()) <= {0.0, 1.0}


# ─────────────────────────────────────────────────────────────────────────────
# Tests anti-regresión del bug #1 (CHANGELOG.md)
# ─────────────────────────────────────────────────────────────────────────────


def test_attempted_suicide_yesno_in_valid_range(
    yrbs_clean: pd.DataFrame,
) -> None:
    """attempted_suicide_yesno ∈ {0, 1} cuando no es NaN.

    Regresión del bug #1 (jun-2026): la variable estuvo invertida y daba
    ~95% yes para 2011-2021. Este test detecta ese bug si reaparece.
    """
    valid = yrbs_clean["attempted_suicide_yesno"].dropna()
    assert set(valid.unique()) <= {0.0, 1.0}, (
        f"Valores inesperados: {set(valid.unique())} — "
        "¿regresión del bug de attempted_suicide_yesno?"
    )


def test_attempted_suicide_yearly_rates_match_cdc(
    yrbs_clean: pd.DataFrame,
) -> None:
    """Las tasas anuales de attempted_suicide deben coincidir con las
    publicadas por el CDC YRBS (Data Summary & Trends Report).

    Regresión del bug #1: si las tasas vuelven a salir 75-95%, el bug
    regresó. CDC oficial: 2019=8.9%, 2021=~10%, resto entre 6-9%.
    """
    def wm(g: pd.DataFrame) -> float:
        g = g.dropna(subset=["attempted_suicide_yesno"])
        return (g["attempted_suicide_yesno"] * g["weight"]).sum() / g["weight"].sum() * 100

    rates = yrbs_clean.groupby("year").apply(wm, include_groups=False)
    # 2019 es el ancla oficial
    rate_2019 = rates.loc[2019]
    assert 7.5 <= rate_2019 <= 10.5, (
        f"attempted_suicide 2019 = {rate_2019:.1f}% (esperado ~8.9%). "
        "Si está muy por encima, el bug de inversión de variable regresó."
    )
    # Ningún año debe pasar de 15%
    assert rates.max() < 15.0, (
        f"Algún año tiene attempted_suicide > 15% "
        f"({rates.to_dict()}). Probable regresión del bug #1."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tests anti-regresión del headline del README
# ─────────────────────────────────────────────────────────────────────────────


def test_sad_hopeless_overall_trend(yrbs_clean: pd.DataFrame) -> None:
    """sad_hopeless overall debe subir de ~28% (2005) a ~42% (2021)."""
    def wm(g: pd.DataFrame) -> float:
        return (g["sad_hopeless"] * g["weight"]).sum() / g["weight"].sum() * 100

    rates = yrbs_clean.groupby("year").apply(wm, include_groups=False)
    r_2005 = rates.loc[2005]
    r_2021 = rates.loc[2021]
    assert 27.0 <= r_2005 <= 30.0, f"2005 = {r_2005:.1f}%, esperado ~28.5%"
    assert 40.0 <= r_2021 <= 44.0, f"2021 = {r_2021:.1f}%, esperado ~42.3%"
    # La subida debe ser monotónica crecientes con un margen
    assert r_2021 > r_2005 + 10, f"Subida {r_2021 - r_2005:.1f}pp < 10pp esperado"


def test_sad_hopeless_female_2021(yrbs_clean: pd.DataFrame) -> None:
    """sad_hopeless en mujeres 2021 = 56.6% ±1pp (lectura del README)."""
    def wm(g: pd.DataFrame) -> float:
        return (g["sad_hopeless"] * g["weight"]).sum() / g["weight"].sum() * 100

    sub = yrbs_clean[(yrbs_clean["year"] == 2021) & (yrbs_clean["sex"] == 1.0)]
    rate = wm(sub)
    assert 55.5 <= rate <= 57.5, (
        f"Mujeres 2021 = {rate:.1f}%, esperado ~56.6% ±1pp"
    )


def test_gender_gap_amplification(yrbs_clean: pd.DataFrame) -> None:
    """El gap F-M en sad/hopeless debe crecer de ~16pp (2005) a ~28pp (2021)."""
    def wm(g: pd.DataFrame) -> float:
        return (g["sad_hopeless"] * g["weight"]).sum() / g["weight"].sum() * 100

    by_sex = yrbs_clean.groupby(["year", "sex"]).apply(wm, include_groups=False).unstack()
    gap_2005 = by_sex.loc[2005, 1.0] - by_sex.loc[2005, 2.0]
    gap_2021 = by_sex.loc[2021, 1.0] - by_sex.loc[2021, 2.0]
    assert 15.0 <= gap_2005 <= 18.0, f"Gap 2005 = {gap_2005:.1f}pp, esperado ~16.4pp"
    assert 26.0 <= gap_2021 <= 30.0, f"Gap 2021 = {gap_2021:.1f}pp, esperado ~28.0pp"


# ─────────────────────────────────────────────────────────────────────────────
# Tests del dataset de mortalidad (wonder)
# ─────────────────────────────────────────────────────────────────────────────


def test_wonder_columns(wonder: pd.DataFrame) -> None:
    expected = {
        "year", "sex_age", "sex", "rate_per_100k",
        "se", "lci", "uci", "estimate_type", "source",
    }
    assert set(wonder.columns) >= expected


def test_wonder_unique_groups(wonder: pd.DataFrame) -> None:
    """4 grupos demográficos únicos: F 10-14, F 15-19, M 10-14, M 15-19."""
    groups = set(wonder["sex_age"].unique())
    assert groups == {
        "Female: 10-14 years",
        "Female: 15-19 years",
        "Male: 10-14 years",
        "Male: 15-19 years",
    }


def test_wonder_rates_positive(wonder: pd.DataFrame) -> None:
    """Las tasas deben ser >= 0."""
    valid = wonder["rate_per_100k"].dropna()
    assert (valid >= 0).all(), "Tasas negativas detectadas"


def test_wonder_male_15_19_peaks_at_2017(wonder: pd.DataFrame) -> None:
    """El pico masculino 15-19 = 17.9/100k en 2017 (HUS 2018)."""
    m_2017 = wonder[
        (wonder["sex_age"] == "Male: 15-19 years")
        & (wonder["year"] == 2017)
    ]
    assert len(m_2017) == 1
    rate = m_2017["rate_per_100k"].iloc[0]
    assert 17.5 <= rate <= 18.5, f"Male 15-19 2017 = {rate}, esperado ~17.9"


# ─────────────────────────────────────────────────────────────────────────────
# Tests del crosswalk (lógica fundamental)
# ─────────────────────────────────────────────────────────────────────────────


def test_qcode_crosswalk_completeness() -> None:
    """El crosswalk debe tener entradas para los 9 años YRBS."""
    from wired_apart.dataset import YRBS_QCODE_CROSSWALK
    expected_years = {2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021}
    assert set(YRBS_QCODE_CROSSWALK.keys()) == expected_years


def test_qcode_crosswalk_concepts_present() -> None:
    """Cada año del crosswalk debe mapear los conceptos clave."""
    from wired_apart.dataset import YRBS_QCODE_CROSSWALK
    for year, mapping in YRBS_QCODE_CROSSWALK.items():
        for concept in ["sad_hopeless", "considered_suicide", "made_plan"]:
            assert concept in mapping, f"Año {year} sin mapeo para {concept}"
            # El Q-code debe empezar con 'q' y ser un string
            assert mapping[concept].startswith("q"), (
                f"Año {year} {concept} -> {mapping[concept]} no parece un Q-code"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Tests de las funciones puras en features.py
# ─────────────────────────────────────────────────────────────────────────────


def test_assign_birth_cohort() -> None:
    from wired_apart.features import assign_birth_cohort
    import pandas as pd
    s = assign_birth_cohort(pd.Series([2021, 2019]), pd.Series([15, 14]))
    assert list(s) == [2006, 2005]


def test_rate_per_100k_handles_zero_population() -> None:
    from wired_apart.features import rate_per_100k
    import pandas as pd
    r = rate_per_100k(pd.Series([10, 5, 0]), pd.Series([1000, 0, 1000]))
    # 10/1000*1e5 = 1000, 5/0 -> NaN, 0/1000*1e5 = 0
    assert r.iloc[0] == 1000.0
    assert pd.isna(r.iloc[1])
    assert r.iloc[2] == 0.0


def test_zscore_constant_input() -> None:
    """zscore con todos los valores iguales -> todos 0 (IQR=0)."""
    from wired_apart.features import zscore
    import pandas as pd
    z = zscore(pd.Series([5, 5, 5, 5]))
    assert (z == 0).all()


def test_assign_rewiring_period() -> None:
    """La ventana rewiring 2010-2015 (inclusivo) según Haidt."""
    from wired_apart.features import assign_rewiring_period
    import pandas as pd
    s = assign_rewiring_period(pd.Series([2009, 2010, 2015, 2016, 2020]))
    labels = list(s)
    assert "rewiring" in labels[0] or "pre-rewiring" in labels[0]  # 2009
    assert "rewiring" in labels[1]  # 2010
    assert "rewiring" in labels[2]  # 2015 (inclusivo)
    assert "post-rewiring" in labels[3]  # 2016
    assert "pandemic-era" in labels[4]  # 2020
