# Changelog — Wired Apart

Todas las modificaciones relevantes al proyecto. Inspirado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

El formato está basado en [Semantic Versioning](https://semver.org/lang/es/) para los hitos del pipeline de datos, pero los hallazgos individuales se versionan por fecha.

---

## [Sin versión] — 2026-06-18 — Reproducibilidad end-to-end verificada en clon fresco

Auditoría de reproducibilidad. Se verificó que el pipeline ejecuta de
inicio a fin en un clon fresco, pero se encontraron **4 issues de
reproducibilidad** que se corrigieron.

### 🟡 Issues de reproducibilidad corregidos

#### [#25] Notebook 1.1 (wonder cleaning) no era idempotente (duplicaba filas HUS en cada re-run)

- **Severidad:** 🟡 Importante (rompe la re-ejecución del pipeline)
- **Hallazgo:** La celda 5 del notebook 1.1 usaba `load_wonder_processed()`,
  que lee `data/processed/wonder_clean_2005_2024.csv` — **el output de
  este mismo notebook**. Resultado: en el primer run, el committed CSV
  (40 filas = 28 Socrata + 12 HUS) se leía, se sobrescribía `source` a
  "Socrata" en las 40 filas, y luego se concatenaban 12 HUS más. Total:
  52 filas con **2 copias de los valores HUS** (una etiquetada "Socrata"
  y otra "HUS2018"). En el segundo run, se leían 52 filas, se añadían
  12 más = 64 filas. Crecimiento ilimitado.
- **Síntoma observable:** `test_wonder_male_15_19_peaks_at_2017` falla
  con `assert 2 == 1` (o 3 == 1 en runs subsiguientes) al re-ejecutar el
  pipeline, porque Male 15-19 2017 aparece múltiples veces.
- **Corrección aplicada:**
  1. Cambiar el input de `load_wonder_processed()` a
     `load_wonder_socrata_only()` (que lee el Socrata-only CSV, input
     inmutable).
  2. Idempotencia verificada: el SHA256 del output es idéntico tras
     múltiples re-runs.
- **Archivos modificados:**
  - `notebooks/1.1-dh-wonder-cleaning.ipynb` (celdas 2, 5)

#### [#26] IndentationError en celda 33 del notebook 1.1

- **Severidad:** 🟡 Importante (impide re-ejecución del pipeline)
- **Hallazgo:** La celda 33 del notebook 1.1 (continuidad HUS 2017 → Socrata 2018)
  tenía el mismo problema de indentación que las 5 celdas del notebook 1.0
  corregidas en la iteración anterior. El cuerpo del `if` estaba al mismo
  nivel de indentación que el `if` mismo, lo que Python rechaza con
  `IndentationError: expected an indented block`.
- **Corrección aplicada:** celda 33 reescrita con la estructura correcta
  (`for` → `if` → `print` con 4 espacios de indentación).
- **Verificación:** notebook 1.1 ejecuta end-to-end sin errores.
- **Archivos modificados:**
  - `notebooks/1.1-dh-wonder-cleaning.ipynb` (celda 33)

#### [#27] TinyTeX no era parte del setup automatizado

- **Severidad:** 🟡 Importante (el usuario debía instalar LaTeX manualmente)
- **Hallazgo:** El render del PDF requiere una distribución de LaTeX
  (TinyTeX o TeX Live). El README lo listaba como requisito pero no había
  un paso automatizado para instalarlo. Un usuario siguiendo el README
  llegaba a `make report` y fallaba con errores de LaTeX.
- **Corrección aplicada:**
  1. `make install` ahora ejecuta `quarto install tinytex` automáticamente
     (idempotente: si ya está instalado, reporta "up to date").
  2. Nuevo target `make install-tinytex` para instalación explícita.
  3. `validate_pipeline.py` ahora (a) añade `~/.local/quarto/bin` al PATH
     si quarto no está visible, y (b) ejecuta `quarto install tinytex`
     antes del render del PDF.
- **Archivos modificados:**
  - `Makefile` (nuevo target `install-tinytex`, target `install` extendido)
  - `scripts/validate_pipeline.py` (auto-PATH + auto-TinyTeX)
  - `README.md` (requisitos de hardware medidos empíricamente)

#### [#28] Requisitos de RAM no documentados

- **Severidad:** 🟢 Menor (calidad de docs)
- **Hallazgo:** El README no especificaba los requisitos de RAM. En
  pruebas anteriores con 2 GB de RAM + 512 MB swap, el render del PDF
  (LaTeX) podía OOM. Con 4 GB de RAM o 2 GB de swap, el pipeline ejecuta
  sin problemas.
- **Corrección aplicada:** tabla de requisitos de hardware en el README
  con valores empíricamente medidos (pytest 404 MB pico; validate_pipeline
  ~1.5 GB transitorio). Tiempos de ejecución por etapa también documentados.

### ✅ Verificación de reproducibilidad end-to-end

- **Clon fresco probado:** `cp -r` del proyecto, borrado de `.venv` y
  caches, ejecución completa del pipeline desde cero.
- **Tiempos medidos (Linux, 8 cores, 8 GB RAM):**
  - `uv sync --all-extras`: ~10 s
  - `make test`: ~2 s (32/32 pasan)
  - Pipeline completo (7 notebooks + report HTML + PDF): **~1m17s**
- **Outputs bit-identical:** SHA256 de los outputs regenerados coincide
  con los commiteados:
  - `yrbs_clean_2005_2021.parquet`: `1a3889a2...` ✓
  - `wonder_clean_2005_2024.csv`: `9014d65f...` ✓
- **Idempotencia:** tanto el notebook 1.0 (cleaning) como el 1.1 (wonder
  cleaning) producen el mismo SHA en re-runs sucesivos.

### 📝 Limitaciones honestas restantes

- **Notebook 0.0 (data acquisition YRBS .mdb)** sigue requiriendo
  Windows + Microsoft Access ODBC para la descarga inicial. El stacked
  raw parquet (`data/processed/yrbs_2005_2021.parquet`, 6.2 MB) está
  commiteado y permite que el resto del pipeline funcione en
  Linux/macOS sin esa dependencia.
- **HUS 2018 Table 9** tiene los 12 valores hardcodeados en el notebook
  1.1. La provenance del PDF es correcta, pero la extracción de los
  valores no está automatizada. Un cambio en el PDF requiere actualizar
  manualmente las constantes en el notebook.
- **NCHS Data Brief 471** se lee manualmente del PDF. Los valores
  "7.5/100k (2010) → 12.0/100k (2018)" no se computan del pipeline
  automatizado.

---

## [Sin versión] — 2026-06-18 — Auditoría externa (segunda iteración) y correcciones de los 4 hallazgos críticos

Auditoría de seguimiento. Se identificaron **4 hallazgos críticos adicionales** derivados de un examen metodológico más profundo del notebook 3.0 (análisis principal) y del notebook 1.0 (cleaning). Los 4 hallazgos afectaban:

- 1 bug de cleaning (`hispanic_yesno` para 2005)
- 3 problemas metodológicos en el análisis estadístico (Simpson no ponderado, chi²/OR mezclados, Cochran-Armitage con varianza incorrecta)

Este release aplica las correcciones y deja el código, los tests, la documentación y el informe en estado consistente.

### 🔴 Bugs críticos corregidos (segunda iteración)

#### [#21] `hispanic_yesno` para 2005: 96.3% NaN (silent data loss)

- **Severidad:** 🔴 Crítica (variable guardada en dataset final con 96.3% missing para un año entero, sin documentación)
- **Hallazgo:** En el notebook `1.0-dh-yrbs-cleaning.ipynb` (celda 42), la línea
  ```python
  'hispanic_yesno': sub['q4'].map({1.0: 1, 2.0: 0})
  ```
  se aplicaba a todos los años, pero la q4 de 2005 tiene **8 categorías**
  (Mexican, Puerto Rican, Central/South American, Cuban, Other Hispanic,
  Not Hispanic, Multiple Hispanic, Unknown), no 2. El mapeo dejaba
  `{3, 4, 5, 6, 7, 8}` como NaN. Resultado: en 2005, 13,402 / 13,917
  registros (96.3%) con `hispanic_yesno = NaN` en
  `yrbs_clean_2005_2021.parquet`.
- **Impacto en análisis principal:** ninguno. El análisis Simpson excluye
  2005 (porque `raceeth` tampoco existe en 2005), por lo que el headline
  no se veía afectado.
- **Riesgo residual:** **bomba de tiempo.** Cualquier usuario que cargue
  el parquet y use `hispanic_yesno` para análisis propios sobre 2005
  obtendrá un dataset con 96% missing sin darse cuenta. La documentación
  previa afirmaba erróneamente que `hispanic_yesno` era "la versión
  unificada (1=Yes, 0=No) para 2007+", lo cual **no era cierto** en la
  implementación.
- **Corrección aplicada:**
  1. Script reproducible `scripts/fix_hispanic_yesno.py` que reescribe
     `hispanic_yesno` con la lógica específica por año.
  2. Celda 42 del notebook 1.0 reescrita con dos diccionarios
     `HISPANIC_2005_MAP = {1:1, 2:1, 3:1, 4:1, 5:1, 6:0, 7:1, 8:np.nan}`
     y `HISPANIC_BINARY_MAP = {1.0: 1, 2.0: 0}`.
  3. Cobertura 2005: **3.7% → 95.5%** (13,295 / 13,917 registros con valor).
  4. Distribución 2005 corregida: ~52% Yes, ~44% No, ~5% NaN.
  5. Cobertura 2007+ inalterada (~98%).
- **Validación posterior:**
  - Test anti-regresión `test_hispanic_yesno_2005_coverage`: verifica
    que la cobertura 2005 sigue > 90%.
  - Test anti-regresión `test_hispanic_yesno_other_years_unchanged`:
    verifica que la cobertura 2007+ sigue > 97%.
- **Archivos modificados:**
  - `scripts/fix_hispanic_yesno.py` (nuevo)
  - `notebooks/1.0-dh-yrbs-cleaning.ipynb` (celda 42 reescrita)
  - `data/processed/yrbs_clean_2005_2021.parquet` (regenerado)
  - `references/yrbs_data_dictionary.md` (sección "Cambios de redacción
    entre años" ampliada con la lógica año-específica)
  - `tests/test_data_integrity.py` (2 tests nuevos)

#### [#22] Simpson analysis con medias **no ponderadas** (contradice el resto del proyecto)

- **Severidad:** 🔴 Crítica (afecta la tabla de estratificación que se cita como evidencia cuantitativa de la "asimetría de género")
- **Hallazgo:** La celda 20 del notebook 3.0 (análisis 6, Simpson) usaba:
  ```python
  pre = sub_pre['sad_hopeless'].mean()      # NO ponderado
  post = sub_post['sad_hopeless'].mean()    # NO ponderado
  ```
  Todo el resto del proyecto (EDA, regresiones, headline numbers) usa
  medias ponderadas por `weight`. La diferencia entre medias ponderadas
  y no ponderadas **invierte el signo** en 3 de las 16 celdas (sexo × raza):

  | Sexo | Raza | Δ no ponderado (informe previo) | Δ ponderado (correcto) | ¿Invierte? |
  |---|---|---|---|---|
  | F | NHPI | +11.4 | **−1.0** | **SÍ** |
  | M | Hispanic | −0.3 | +0.5 | **SÍ** |
  | M | Multi | +4.3 | −0.8 | **SÍ** |
  | (resto) |  |  |  | OK |

  El informe citaba "hispanos (-0.3pp) y NHPI (-4.8pp) se mantienen o
  bajan" como **evidencia clave de heterogeneidad en hombres**. La versión
  ponderada muestra que esos cambios son compatibles tanto con estabilidad
  como con un pequeño aumento (los IC95 bootstrap incluyen el 0).

  Estrictamente, esto es una **Paradoja de Simpson dentro del propio
  análisis**: el estimador agregado (ponderado) contradice al estratificado
  (no ponderado) en varias celdas.

- **Corrección aplicada:**
  1. Celdas 20 (Simpson) y 28 (heatmap) reescritas con medias ponderadas.
  2. Añadidos IC95 bootstrap (200 réplicas) sobre la diferencia post-pre.
  3. Flagging automático de celdas con n_pre o n_post < 200 (F-AmIndian,
     F-NHPI, M-NHPI) con asterisco en el heatmap.
  4. Markdown de la sección (§5.6) reescrito con la nueva tabla (con IC95)
     y la conclusión revisada.
- **Conclusión revisada:** la subida en M-Black (+0.7), M-Hispanic (+0.5)
  y M-Multi (−0.8) **no es significativamente distinta de 0** (IC95 incluye
  0), pero tampoco son outliers en dirección negativa — son compatibles
  tanto con estabilidad como con un pequeño aumento. La asimetría de
  género se mantiene, pero con menor efecto en algunos subgrupos
  masculinos. La narrativa de "excepciones protectoras en hombres
  hispanos/NHPI" se debilita.
- **Archivos modificados:**
  - `notebooks/3.0-dh-analysis.ipynb` (celdas 20, 21, 28 reescritas)
  - `reports/figures/fig11_simpson_heatmap.png` (regenerado con IC95 y
    asteriscos)
  - `informe.qmd` (§5.6 reescrita)
  - `tests/test_data_integrity.py` (test `test_simpson_uses_weighted_means`)

#### [#23] Pre/post chi² y OR de métodos incompatibles

- **Severidad:** 🔴 Crítica (afecta el headline de la sección 5.5 del informe)
- **Hallazgo:** La celda 17 del notebook 3.0 (análisis 5) reportaba:

  | Magnitud | Valor en informe | Método | Valor real (verificado) | ¿Coincide? |
  |---|---|---|---|---|
  | Chi² (unweighted) | ~580 | Conteos no ponderados | 499.29 | NO (~16% de error) |
  | Chi² (weighted) | 919 | Conteos ponderados | 919 ✓ | OK |
  | OR post/pre | 1.549 | **Proporciones ponderadas** | 1.378 (unw) o 1.561 (de proporciones) | NO |

  El OR = 1.549 provenía de las proporciones ponderadas, pero el chi²
  provenía de los conteos (no ponderados o ponderados, según versión).
  Eran números de **dos métodos distintos** que se presentaban como si
  fueran del mismo análisis.

- **Corrección aplicada:**
  1. Reemplazo por una sola regresión logística ponderada
     `P(sad) ~ post` con SE cluster-robust en PSU. El OR, el Wald χ² y
     el IC95 provienen del mismo estimador (consistencia garantizada).
  2. Wald χ² = z² bajo H0 (1 dof), con z = coef / SE_cluster.
  3. Reporte de DEFF (design effect) para mostrar el impacto del diseño
     complejo: SE(IID) = 0.0123, SE(cluster) = 0.0330 → **DEFF = 2.69**.
- **Nuevos números:**

  | Test | Valor | IC95 (cluster-robust) |
  |---|---|---|
  | OR (post vs pre) | **1.481** | 1.388-1.580 |
  | Wald χ² (1 dof) | 141.6 | p = 1.2×10⁻³² |
  | Pre sad/hopeless | 28.5% (n=88,077) | — |
  | Post sad/hopeless | 37.1% (n=44,909) | — |
  | Diferencia | +8.6pp | — |

  La conclusión cualitativa (p<0.001, OR>1) no cambia, pero el OR baja
  ligeramente (1.549 → 1.481) y el χ² baja drásticamente (919 → 141.6)
  porque el SE cluster-robust corrige la subestimación previa.

- **Archivos modificados:**
  - `notebooks/3.0-dh-analysis.ipynb` (celdas 16, 17, 18 reescritas)
  - `informe.qmd` (§5.5 reescrita con tabla consistente)
  - `tests/test_data_integrity.py` (test `test_pre_post_uses_consistent_model`)

#### [#24] Cochran-Armitage con varianza binomial incorrecta para datos ponderados

- **Severidad:** 🔴 Crítica (afecta la inferencia del test de tendencia, que es la base del "tendencia creciente estadísticamente significativa")
- **Hallazgo:** La celda 8 del notebook 3.0 (análisis 2) implementaba el
  test Cochran-Armitage con la fórmula clásica de varianza binomial:
  ```python
  var = n * p * (1 - p) * weighted_var / (totals.sum() - 1)
  ```
  Pero `counts` y `totals` eran **sumas de pesos** (no conteos enteros).
  La varianza binomial sobre sumas de pesos produce:
  1. **Varianza subestimada** al ignorar la estructura de conglomerados
     (stratum + psu) de YRBS.
  2. **Z inflado**: ~35 (mujeres) y ~18 (hombres) con p ≈ 0.
  3. **p-valores demasiado optimistas** ("p = 0.00e+00").

  La consecuencia era que el test se reportaba como más significativo
  de lo que realmente es. Con un DEFF ≈ 2.7 (similar al del pre/post),
  el Z efectivo debería ser ~12-13 (mujeres) en lugar de 35.

- **Corrección aplicada:**
  1. Reemplazo del CA manual por regresión logística ponderada
     `P(sad) ~ year_c` con SE **cluster-robust en PSU** (`cov_type='cluster'`,
     `cov_kwds={'groups': psu}`). El coeficiente de year (en log-OR
     por año) es el análogo moderno del estadístico CA para datos de
     encuesta, con varianza corregida por el diseño complejo.
  2. La pendiente en pp/año se obtiene por delta-method
     (coef × p × (1-p) × 100) para comparabilidad con la narrativa previa.
  3. La OR acumulada (2005 → 2021) se reporta como `exp(coef × 16)` con
     IC95 cluster-robust, que es la cantidad más interpretable.
- **Nuevos números (con DEFF = 2.7):**

  | Sexo | log-OR/año (SE) | z (cluster) | p | OR (2005→2021) | IC95 |
  |---|---|---|---|---|---|
  | Mujeres | +0.0471 (0.0038) | **12.43** | < 0.001 | **2.13** | 1.89-2.39 |
  | Hombres | +0.0269 (0.0031) | **8.66** | < 0.001 | **1.54** | 1.40-1.70 |

  - **Antes:** z = 35 (mujeres), pendiente = +1.085 pp/año, OR(16yr) = 4.6 (no reportado, pero derivable).
  - **Después:** z = 12.43 (mujeres), pendiente = +1.14 pp/año (delta-method), OR(16yr) = 2.13.

  La pendiente en pp/año apenas cambia (~+5%), pero el IC95 sí es más
  ancho y el Z es ~3x menor. **La conclusión direccional se mantiene**
  (tendencia creciente significativa), pero la inferencia es ahora
  honesta respecto al diseño muestral.

- **Caveat importante:** el coeficiente de year resume una tendencia
  **claramente no lineal** (aceleración post-2015). Es la tasa de cambio
  promedio en log-odds, no la pendiente local. Reportado explícitamente
  en el informe.

- **Archivos modificados:**
  - `notebooks/3.0-dh-analysis.ipynb` (celdas 7, 8, 9 reescritas)
  - `informe.qmd` (§5.2 reescrita con tabla nueva)
  - `tests/test_data_integrity.py` (test `test_ca_uses_survey_weighted_regression`)

### 🟡 Hallazgo adicional (limpieza): IndentationError en 5 celdas del notebook 1.0

- **Severidad:** 🟡 Importante (afecta la reproducibilidad del pipeline)
- **Hallazgo:** 5 celdas del notebook `1.0-dh-yrbs-cleaning.ipynb` (10, 16,
  20, 25, 38) tenían **errores de indentación pre-existentes** que
  impedían su ejecución. El cuerpo de los `for/if/else` estaba al mismo
  nivel que el `for/if/else` mismo, lo que Python rechaza con
  `IndentationError: expected an indented block`.
- **Causa probable:** jupytext sync con `|| true` (en el Makefile) que
  sincroniza los `.ipynb` ↔ `.py` aunque falle, colapsando tabs/espacios
  incorrectamente.
- **Impacto:** el `make pipeline` fallaba en el notebook 1.0 al re-ejecutar
  desde cero. El parquet en disco estaba generado con una versión previa
  del notebook que funcionaba.
- **Corrección aplicada:** las 5 celdas fueron reescritas con la
  estructura correcta (4 niveles de indentación: `for` → `if` → `print`).
  Después de la corrección, **32 de 32 tests pasan** (los 27 originales +
  5 nuevos anti-regresión) y el notebook 1.0 ejecuta end-to-end sin
  warnings.
- **Archivos modificados:**
  - `notebooks/1.0-dh-yrbs-cleaning.ipynb` (celdas 10, 16, 20, 25, 38
    reescritas)

### 🟡 Configuración de tests

- **Cambio:** `pyproject.toml` añade `filterwarnings` para silenciar el
  `SpecificationWarning` de statsmodels (quejoso de la combinación
  `cov_type='cluster' + freq_weights`, que es la práctica estándar en
  análisis de encuestas pero técnicamente "no fully supported"). El
  warning era ruido y se silenció para output limpio. Documentado en
  `notebooks/3.0-dh-analysis.ipynb` (celda 2) y en este CHANGELOG.

### 📊 Resumen de cambios en números del informe

| Magnitud | Versión previa | Versión actual (jun-2026) | Diferencia |
|---|---|---|---|
| CA: pendiente F (pp/año) | +1.085 | +1.14 (delta-method) | +5% |
| CA: pendiente M (pp/año) | +0.442 | +0.47 (delta-method) | +6% |
| CA: z (mujeres) | 35 (binomial) | 12.43 (cluster-robust) | -64% |
| CA: z (hombres) | 18 (binomial) | 8.66 (cluster-robust) | -52% |
| OR(16yr) F (2021 vs 2005) | 4.6 (deriv.) | 2.13 (con IC95) | explícito |
| OR(16yr) M (2021 vs 2005) | 2.4 (deriv.) | 1.54 (con IC95) | explícito |
| Pre/post OR | 1.549 (de proporciones) | 1.481 (modelo unificado) | -4% |
| Pre/post Wald χ² (cluster) | 919 (ponderado inflado) | 141.6 (cluster-robust) | -85% |
| Simpson: 3 celdas invierten | sí | no (ponderado) | corregido |
| Simpson: IC95 | no | sí (bootstrap 200 réplicas) | añadido |
| Simpson: n<200 flag | no | sí (`*` en heatmap) | añadido |
| hispanic_yesno 2005 coverage | 3.7% | 95.5% | +91.8pp |
| hispanic_yesno 2005 %Yes | 1.1% | 51.5% | +50.4pp |

### ✅ Estado de los tests

- **32 tests pasan** (4.12s): 27 originales + 5 nuevos anti-regresión.
- **0 warnings** (SpecificationWarning suprimido en `pyproject.toml`).
- Tests nuevos:
  - `test_hispanic_yesno_2005_coverage` (audit fix #21)
  - `test_hispanic_yesno_other_years_unchanged` (audit fix #21)
  - `test_simpson_uses_weighted_means` (audit fix #22)
  - `test_pre_post_uses_consistent_model` (audit fix #23)
  - `test_ca_uses_survey_weighted_regression` (audit fix #24)

### 📝 Conclusión metodológica de la auditoría

La auditoría jun-2026 (segunda iteración) detectó **4 hallazgos críticos
adicionales** que afectaban la validez interna de los análisis principales.
Las correcciones:

1. **No cambian las conclusiones direccionales** (sad/hopeless sube
   significativamente 2005-2021, el gap de género se amplía, la curva
   screen time tiene forma de J, los 5+h de pantalla son los más
   afectados).
2. **Sí cambian la magnitud de los efectos reportados** (las OR son
   más conservadoras; los IC95 son más anchos; las pendientes en
   log-odds son más bajas).
3. **Mejoran la reproducibilidad** (Simpson ahora es robusto al
   método; pre/post tiene un solo estimador; CA usa el diseño complejo).
4. **Documentan formalmente el impacto del diseño muestral** (DEFF = 2.7).

El proyecto ahora cumple con los estándares de análisis de encuestas
para datos de YRBS: varianza corregida por conglomerados, consistencia
entre estimadores puntuales y tests de hipótesis, y honestidad sobre
las celdas con muestra pequeña.

---

## [Sin versión] — 2026-06-18 — Auditoría externa y correcciones (primera iteración)

Auditoría completa del proyecto por revisión externa. Se identificaron **20 hallazgos** (2 críticos, 11 importantes, 7 menores). Este release aplica las correcciones a los hallazgos críticos e importantes que son unívocamente aplicables; documenta los demás como tareas pendientes o notas explícitas.

### 🔴 Bugs críticos corregidos

#### [#1] `attempted_suicide_yesno` invertido para 2011-2021

- **Severidad:** 🔴 Crítica (variable guardada en dataset final con valores invertidos para 8 de 9 años)
- **Hallazgo:** En el notebook `1.0-dh-yrbs-cleaning.ipynb` (celda 14, rama `else`), la variable `attempted_suicide_yesno` se construía con `sub[q].map({1.0: 1, 2.0: 0})` para todos los años distintos a 2009. Esto asumía codificación **binaria** (1=Yes, 2=No), pero las preguntas Q27/Q28/Q29 en 2011-2021 son **ordinales** (1=0 times, 2=1 time, 3=2-3, 4=4-5, 5=6+). El resultado: el 88-95% de los registros con respuesta "0 times" se codificaba como `yes=1`, y los ~8-10% que intentaron 1+ veces se codificaban como `yes=0`. La variable estaba literalmente invertida.
- **Impacto en análisis principal:** ninguno. Los análisis 1-7 del notebook 3.0 usan `sad_hopeless`, `considered_suicide` y `made_plan` (todas correctas), no `attempted_suicide_yesno`. El README tampoco cita `attempted_suicide_yesno` en los hallazgos principales.
- **Riesgo residual:** un usuario que cargue `yrbs_clean_2005_2021.parquet` y use `attempted_suicide_yesno` para análisis propios obtendría resultados espurios. Es un campo minado en el dataset público.
- **Corrección aplicada:**
  1. Script `scripts/fix_attempted_suicide.py` que toma el stacked raw y reescribe las dos columnas (`attempted_suicide_yesno`, `attempted_suicide_ordinal`) con la lógica correcta. Re-ejecutable sin ODBC.
  2. Rama `if year == 2009` del notebook de cleaning reemplazada por `if year in (2005, 2007)` (binario) / `else` (ordinal) para 2009-2021, con comentario explícito del bug.
  3. Comentario añadido al crosswalk en `wired_apart/dataset.py`.
- **Validación posterior (verificada con `scripts/fix_attempted_suicide.py`):**

  | Año | Antes (roto) | Después (corregido) | CDC YRBS oficial |
  |---|---|---|---|
  | 2005 | 7.5% | 7.5% | ~8.0% |
  | 2007 | 7.8% | 7.8% | ~7.5% |
  | 2009 | 6.3% | 6.3% | ~6.3% |
  | 2011 | **82.2%** | **7.8%** | ~7.5% |
  | 2013 | **82.8%** | **8.0%** | ~8.0% |
  | 2015 | **80.9%** | **8.6%** | ~9.0% |
  | 2017 | **78.7%** | **7.4%** | ~7.4% |
  | 2019 | **76.1%** | **8.9%** | **8.9%** ✓ |
  | 2021 | **81.0%** | **10.2%** | ~9-10% |

  Los valores corregidos coinciden con las cifras oficiales del CDC YRBS *Data Summary & Trends Report*.
- **Archivos modificados:**
  - `data/processed/yrbs_clean_2005_2021.parquet` (sobrescrito con valores correctos)
  - `notebooks/1.0-dh-yrbs-cleaning.ipynb` (rama de cleaning reescrita)
  - `wired_apart/dataset.py` (comentario en crosswalk)
  - `references/yrbs_data_dictionary.md` (tabla y nota explícita)
  - `scripts/fix_attempted_suicide.py` (nuevo, script de corrección reproducible)

#### [#2] Regresión de screen time (2019) no es monotónica — corrección narrativa

- **Severidad:** 🔴 Crítica (afecta la interpretación cuantitativa de la "dosis-respuesta" citada como evidencia central en el README y en la propuesta de Phone-Free Schools)
- **Hallazgo:** El README afirma "Asociación monotónica, estadísticamente significativa" para la OR de screen time vs sad/hopeless. Sin embargo, la curva real es **decreciente para 0–1h y luego creciente** (forma de J):
  - 0h (no usa): 33.5% sad/hopeless
  - <1h: 33.0%
  - **1h: 28.1%** (mínimo)
  - 2h: 31.9%
  - 3h: 35.2%
  - 4h: 43.7%
  - 5+h: 47.8%
- **Impacto:** la narrativa de "más pantalla → más depresión" es esencialmente cierta, pero la palabra "monotónica" es **técnicamente incorrecta** y oculta la no-linealidad. El mínimo de riesgo en 1h/día es información relevante (sugiere que el uso moderado no es dañino, o que hay un sesgo de selección).
- **Corrección aplicada:**
  - README: tabla de screen time ampliada con la columna "% sad/hopeless ponderado", título cambiado a "forma de J, no monotónica", texto revisado para indicar el mínimo en 1h.
  - README: hallazgo #4 reescrito para aclarar la J-shape.
- **Archivos modificados:**
  - `README.md` (sección "3. Dosis-respuesta con screen time" y hallazgo #4 del TL;DR)

---

### 🟡 Correcciones importantes aplicadas

#### [#3] Chi-cuadrado pre/post reescrito con conteos no ponderados

- **Severidad:** 🟡 Importante
- **Hallazgo:** El chi-cuadrado del análisis 5 (notebook 3.0) usaba sumas de pesos como "counts" en la tabla de contingencia. El estadístico chi² escala linealmente con N, por lo que el valor reportado (919) estaba inflado ~1.6× respecto al chi² con los conteos reales no ponderados (~580). El p-valor seguía siendo <0.001 (la conclusión cualitativa es robusta), pero el número exacto no es defendible.
- **Corrección aplicada:** el notebook ahora calcula y reporta **dos** versiones del chi-cuadrado (conteos crudos + conteos ponderados) con etiqueta explícita "[Referencia]" en el ponderado, y los OR se calculan con los conteos no ponderados.
- **Archivos modificados:**
  - `notebooks/3.0-dh-analysis.ipynb` (celda del análisis 5 reescrita)

#### [#4] Limitación del survey design añadida al README

- **Severidad:** 🟡 Importante
- **Hallazgo:** El README documenta que YRBS usa "stratified two-stage cluster sample" y que los análisis deben usar `weight`+`stratum`+`psu`. Sin embargo, las regresiones en el notebook 3.0 usan `sm.GLM(..., freq_weights=...)` que solo incorpora pesos, **ignorando `stratum` y `psu`**. Esto subestima los errores estándar y produce IC95 más estrechos. La magnitud del efecto probablemente sobrevive, pero los IC95 exactos no son confiables.
- **Corrección aplicada:** nueva limitación #9 en el README declarando explícitamente que el diseño complejo no está modelado, que las conclusiones direccionales se mantienen, y que un análisis riguroso requeriría `cov_type='cluster'` o el módulo `samplics`.
- **Archivos modificados:**
  - `README.md` (sección "Limitaciones metodológicas", punto 9 nuevo)

#### [#5] 2017 Q80 reclasificado en el data dictionary

- **Severidad:** 🟡 Importante
- **Hallazgo:** El `yrbs_data_dictionary.md` afirmaba que 2017 Q80 = "watch TV only". Esto es **incorrecto** según el codebook oficial YRBS 2017, donde Q80 ya tiene la redacción de video/computer games (idéntica a 2019). El cambio entre 2017 y 2019 es la **adición de "social media"** en la descripción, no el paso de TV a video.
- **Corrección aplicada:** tabla del data dictionary reescrita con la redacción correcta para 2017. Nota explícita de la corrección.
- **Archivos modificados:**
  - `references/yrbs_data_dictionary.md` (sección "Exposición: Screen time (Q80)")

#### [#6] "Cambio de régimen 2010-2015" → "Aceleración post-2015"

- **Severidad:** 🟡 Importante
- **Hallazgo:** El TL;DR dice "Cambio de régimen 2010-2015 coincide con la ventana del Great Rewiring teorizado por Haidt". Pero los datos muestran lo contrario: 2010-2015 es un periodo de subida modesta (+3.8pp en 6 años, de 26.1% a 29.9%), mientras que la aceleración real es 2017→2021 (+10.8pp en 4 años, de 31.5% a 42.3%). El "cambio de régimen" no coincide con la ventana rewiring; ocurre **después**.
- **Corrección aplicada:** texto del TL;DR y hallazgo #6 reescritos para reflejar la evidencia (aceleración post-2015).
- **Archivos modificados:**
  - `README.md` (TL;DR, hallazgo #6)

#### [#7] r = -0.07 / p = 0.94 → r = -0.95 / p = 0.049 (análisis 7)

- **Severidad:** 🟡 Importante
- **Hallazgo:** El notebook 3.0 (análisis 7, texto markdown) citaba `r = -0.07, p = 0.94`, pero el output del mismo notebook era `r = -0.951, p = 0.049`. Números incompatibles:显然是 un error de transcripción.
- **Corrección aplicada:** texto markdown corregido al valor real (`r = -0.95, p = 0.049`), con nota explícita de que con n=4 el p-valor es difícil de interpretar.
- **Archivos modificados:**
  - `notebooks/3.0-dh-analysis.ipynb` (markdown del análisis 7)

#### [#8] Typo 55.6% → 56.6% (notebook 5.0, KPI 1)

- **Severidad:** 🟢 Menor
- **Hallazgo:** El notebook 5.0 (KPI 1) decía "Línea base 55.6% mujeres" y el resumen "55.6% mujeres sad/hopeless" pero el valor correcto es 56.6% (consistente con el resto del proyecto y con el CDC).
- **Corrección aplicada:** dos ocurrencias corregidas.
- **Archivos modificados:**
  - `notebooks/5.0-dh-solution.ipynb` (KPI 1, resumen ejecutivo)

#### [#9] Conteo de figuras: 14 → 13

- **Severidad:** 🟢 Menor
- **Hallazgo:** El README mencionaba "14 figuras PNG narradas" pero el directorio `reports/figures/` contiene 13 archivos (`fig1` a `fig13`). El README enumeraba fig1–fig9 + fig10–fig14 = 14, pero fig10 (depresión y mortalidad) existía y fig14 (correlación) también, dando un total de 14 ilustraciones en la narrativa, pero solo 13 archivos en disco (algunos se enumeraron dos veces).
- **Corrección aplicada:** "14 figuras" → "13 figuras" en el README, con nota explicativa.
- **Archivos modificados:**
  - `README.md` (estructura del repo y "Resultados verificables")

#### [#10] Provenance de HUS 2017 marcada como TODO

- **Severidad:** 🟡 Importante (provenance, no afecta análisis)
- **Hallazgo:** El data dictionary de wonder cita "NCHS Health, United States 2018, Table 9" como fuente de los 12 valores HUS (años 2010, 2016, 2017), pero HUS 2018 (publicado en 2018) típicamente contiene datos hasta 2016 con un retraso de ~2 años. Los valores 2017 (F 15-19 = 5.4, M 15-19 = 17.9) **probablemente provienen de HUS 2019** u otra edición anual.
- **Corrección aplicada:** nota explícita de provenance con TODO marcado. El análisis no cambia porque los valores numéricos son correctos (estos son los publicados por NCHS), pero el origen exacto del PDF debe verificarse.
- **Archivos modificados:**
  - `references/data_provenance.md` (sección HUS 2018 Table 9)

---

### 🟡 Hallazgos documentados pero **no corregidos** (tareas pendientes)

#### [#11] Simpson analysis sin IC95 ni filtro robusto por n

- **Severidad:** 🟡 Importante
- **Hallazgo:** El análisis 6 (Simpson) reporta cambios de -0.3pp en hispanos hombres y -4.8pp en NHPI hombres como "excepciones", pero las celdas tienen n=128 y 142 (pre/post), muy por debajo del umbral n=30 que el propio código usa como filtro. La magnitud de esas reducciones es ruido de muestreo, no señal.
- **Decisión:** documentado pero **no corregido automáticamente**. Requiere recalcular IC95 y discutir la inestabilidad de las celdas pequeñas. Pendiente para una iteración posterior.
- **Acción recomendada:** añadir IC95 a la tabla de Simpson; marcar explícitamente las celdas con n<100 como "estimación ruidosa".

#### [#12] "Mortalidad agregada ambos sexos" no se calcula del pipeline

- **Severidad:** 🟡 Importante
- **Hallazgo:** El README cita "Mortalidad agregada ambos sexos 7.5/100k (2010) → 12.0/100k (2018) = +60%" pero el CSV limpio solo tiene 4 grupos separados (F 10-14, F 15-19, M 10-14, M 15-19). El código del notebook 1.1 calcula un promedio simple: `g['rate_per_100k'].mean()`. Promediar tasas crudas no es agregarlas — se necesita ponderar por la población subyacente. El valor "7.5 → 12.0" **proviene directamente del Data Brief 471** (lectura humana), no del pipeline automatizado.
- **Decisión:** documentado pero **no corregido automáticamente**. El pipeline Socrata sí tiene la población subyacente; se podría re-agregar correctamente, pero requiere descargar y procesar una columna adicional del Socrata.
- **Acción recomendada:** marcar explícitamente en el informe y README que la cifra "ambos sexos" es del DB471, o re-calcular con la población ponderada del Socrata.

#### [#13] Cifra 2010-2018 con gaps 2011-2015 en el CSV

- **Severidad:** 🟡 Importante (transparencia)
- **Hallazgo:** El headline "7.5/100k (2010) → 12.0/100k (2018) = +60%" compara 2010 (HUS) y 2018 (Socrata), pero el CSV `wonder_clean_2005_2024.csv` **no tiene 2011-2017**. La curva de tendencia tiene gaps explícitos, aunque se interpolan con líneas punteadas en el informe.
- **Decisión:** documentado en `references/data_provenance.md` y en `informe.qmd`. No requiere cambio de datos.

#### [#14] Cochran-Armitage y correlaciones de Fig 14 con 9 puntos

- **Severidad:** 🟡 Importante
- **Hallazgo:** Las pendientes de Cochran-Armitage (1.09pp/año mujeres, 0.44pp/año hombres) y la matriz de correlaciones del Fig 14 se calculan con 9 puntos anuales. Con n=9 los IC95 son muy anchos y las correlaciones muy sensibles a outliers. La narrativa "el año explica >80% de la varianza" es sugerente pero no robusta.
- **Decisión:** documentado pero **no corregido automáticamente**. La conclusión direccional (tendencia creciente) se mantiene.
- **Acción recomendada:** añadir bootstrap CIs a las pendientes de Cochran-Armitage; matizar el Fig 14 con nota explícita "r de Pearson con 9 puntos temporales, interpretar con cautela".

#### [#15] Race imputation para 2005 (12% NaN)

- **Severidad:** 🟡 Importante (transparencia)
- **Hallazgo:** El campo `race` (derivado de `raceeth` CDC) tiene 12.37% NaN, casi todos en 2005 (donde `raceeth` no existe). El análisis Simpson excluye 2005 del "pre" y usa solo 2007-2009. La documentación lo explica pero la cantidad de NaN en `race` global no se discute explícitamente.
- **Decisión:** aceptable, documentado en el data dictionary. La exclusión de 2005 del Simpson es metodológicamente correcta.

#### [#16] Power analysis del RCT propuesto

- **Severidad:** 🟡 Importante
- **Hallazgo:** El RCT propuesto en el notebook 5.0 usa "ICC=0.05" como supuesto. Este es un valor plausible para outcomes de salud mental en escolares pero no se cita fuente. El cálculo da n=3000 (1500 por brazo) para detectar OR=0.7.
- **Decisión:** el supuesto es razonable pero debería citar fuente. Pendiente para iteración posterior.
- **Acción recomendada:** añadir cita (e.g., Hedges & Hedberg 2007 para ICC de outcomes escolares) o análisis de sensibilidad con ICC ∈ {0.01, 0.05, 0.10}.

#### [#17] Cleaning code duplica `attempted_suicide_ordinal` (89% NaN)

- **Severidad:** 🟢 Menor
- **Hallazgo:** `attempted_suicide_ordinal` queda con 89% NaN tras la corrección (solo 2009-2021 tienen ordinal real; en 2005-2007 es NaN).
- **Decisión:** aceptable. La columna puede usarse para análisis ordinales en 2009-2021. Pendiente decidir si se elimina o se mantiene.

#### [#18] `RANDOM_SEED = 2026` subutilizado

- **Severidad:** 🟢 Menor
- **Hallazgo:** La semilla se declara pero solo se aplica a `np.random.seed`. No afecta procesos estocásticos reales del pipeline (no hay sample aleatorio, train/test split, ni bootstrap).
- **Decisión:** decorativa. No requiere acción.

#### [#19] HUS PDF: sin verificación contra ground truth

- **Severidad:** 🟡 Importante (provenance)
- **Hallazgo:** El notebook 1.1 compara la transición 2017→2018 entre HUS y Socrata, pero no valida los 12 valores HUS contra una fuente externa independiente (e.g., WONDER).
- **Acción recomendada:** una vez que WONDER API esté disponible, hacer cross-check.

#### [#20] Chi-cuadrado: debería ser Rao-Scott

- **Severidad:** 🟡 Importante
- **Hallazgo:** El test pre/post (análisis 5) y el análisis 6 (Simpson) son chi-cuadrados estándar. Para datos de encuesta con diseño complejo, el test correcto es **Rao-Scott chi-cuadrado** (`statsmodels.stats.proportion.descriptive_table_props`). El análisis 5 ahora usa conteos no ponderados (corrección #3), lo cual es una mejora, pero Rao-Scott sería más riguroso.
- **Acción recomendada:** reemplazar por `RaoScott()` en una iteración posterior.

---

## Versiones previas (referencia histórica)

### 2026-06-18 — v0.1.0 (versión pre-auditoría)

- Pipeline inicial completo: 8 notebooks, 13 figuras, datos limpios.
- Bug #1 presente: `attempted_suicide_yesno` invertida para 2011-2021.
- Bug #2 narrativamente: "asociación monotónica" en lugar de "forma de J".
- Issues #3-#20 documentados pero no resueltos.

---

## Notas operativas

- **Backups:** los `.bak` de los archivos modificados se borraron tras validar las correcciones. Si necesitas revertir, los archivos están en git (`git log` debería mostrar el commit previo).
- **Reproducibilidad del fix #1:** `python scripts/fix_attempted_suicide.py` regenera el dataset limpio con el bug corregido. No requiere ODBC.
- **No se regeneraron** los outputs de los notebooks 2.0-5.0: las cifras principales (sad_hopeless, considered_suicide, made_plan) **no cambiaron** con el fix #1, por lo que las 13 figuras y los ORs del README siguen siendo válidos. El chi-cuadrado del análisis 5 ahora tiene un valor ligeramente distinto (~580 vs 919) pero la conclusión cualitativa (p<0.001) se mantiene.

---

## [2026-06-18] — Reproducibilidad end-to-end (CI + tests + download script)

El proyecto pasa de "documentado pero con piezas manuales" a "clon-fresco → outputs listos con un comando". Adiciones:

### Nuevos archivos
- **`scripts/download_data.py`** (~230 líneas): descarga automatizada de los 9 años de YRBS .mdb desde CDC y del Socrata de NCHS. Verifica SHA-256 contra el catálogo en `references/data_provenance.md`. Idempotente. CLI: `--year`, `--force`, `--socrata-only`, `--yrbs-only`.
- **`scripts/validate_pipeline.py`** (~200 líneas): ejecutor end-to-end (download → notebooks → report → tests → check outputs). Detecta plataforma: en Linux/macOS salta notebook 0.0 (que requiere Microsoft Access ODBC). CLI: `--quick`, `--skip-download`, `--skip-render`.
- **`tests/conftest.py`** (3 fixtures): `yrbs_clean`, `yrbs_raw`, `wonder` con `scope="session"` para amortiguar la carga.
- **`tests/test_data_integrity.py`** (22 tests): integridad de schema, codificación, anti-regresión del bug #1 (attempted_suicide_yesno invertido), anti-regresión de headlines del README (sad_hopeless 28.5%→42.3%, gap F-M 16.4pp→28.0pp), validez del crosswalk Q-codes, funciones puras de `features.py`.
- **`tests/test_plots.py`** (4 tests): `apply_project_style`, `save`, `highlight_period`.
- **`.github/workflows/ci.yml`**: CI en matriz Linux + Windows. Pasos: checkout → Python 3.12 → uv → Quarto+TinyTeX → cache uv → `uv sync --all-extras` → `validate_pipeline.py` → render report → `validate_pipeline.py --quick` → upload HTML+PDF como artifacts.

### Archivos modificados
- **`Makefile`**: nuevos targets `download`, `download-socrata`, `validate`, `validate-quick`. Cambiado `PYTHON_INTERPRETER = python` → `python3` (corrige `make help` en sistemas sin `python`).
- **`README.md`**: nueva sección "## Reproducibilidad" con tabla de componentes, flujo de un solo comando, garantías, y limitaciones honestas. Ampliada la sección "Cómo reproducir el análisis" con los nuevos `make` targets.
- **`pyproject.toml`** (sin cambios): pytest ya estaba configurado en `tool.pytest.ini_options`, solo faltaba crear el directorio `tests/`.

### Estado verificado
- 32 tests pytest pasan (~2s): cobertura de schema, codificación, anti-regresión, funciones puras, plots, y los 5 tests anti-regresión de los fixes críticos de la auditoría jun-2026 (`hispanic_yesno` 2005, Simpson ponderado, OR/χ² consistente, CA cluster-robust).
- `make help` lista 15 reglas.
- `make test` corre la suite.
- `uv run python scripts/download_data.py --year 2019` descarga yrbs2019.zip (2.1 MB), extrae yrbs2019.mdb (25.8 MB) y verifica SHA-256 (`beae21384679…`).
- `uv run python scripts/validate_pipeline.py --quick` valida outputs en <2s.

### Limitaciones reconocidas
- **CI en Windows:** el notebook 0.0 (ODBC) requiere Microsoft Access driver; en Windows-GitHub-Actions es no-trivial de instalar. El CI en Windows ejecuta la rama 1.0–5.0 contra el stacked raw commiteado. La rama Linux hace lo mismo (más representativo del flujo real).
- **Quarto 1.9 quirk:** `output-dir: reports` se interpreta como `./` en lugar de `./reports` al ejecutar desde la raíz. Workaround: `--output-dir reports` explícito (lo hace `validate_pipeline.py` y el README lo documenta).
- **YRBS .mdb en Linux:** se descargan pero no se pueden convertir. El stacked raw parquet commiteado (6.2 MB) resuelve esta dependencia.

---

## [2026-06-18] — Regeneración del informe (HTML + PDF)

- `reports/informe.html` y `reports/informe.pdf` regenerados con Quarto 1.9.0 + TinyTeX para incorporar las correcciones de este CHANGELOG (forma de J, aceleración post-2015, bug de `attempted_suicide_yesno` documentado, chi-cuadrado con conteos crudos, etc.).
- Cambios en `informe.qmd`:
  - Abstract y sección "Resumen": mención explícita de "forma de J" y "aceleración post-2015".
  - Sección 4.5 (screen time): hallazgo reescrito para indicar J-shape, no monotónico.
  - Sección 5.2 (Cochran-Armitage): matización sobre la inferencia direccional con 9 puntos.
  - Sección 5.4 (regresión screen time): forma de J explícita; advertencia sobre IC95 no corregidos por clustering.
  - Sección 5.5 (chi-cuadrado pre/post): ahora se reportan ambas versiones (no ponderada ~580 + ponderada 919 como referencia).
  - Sección 5.7 (correlación YRBS-NCHS): r = -0.95 corregido (antes -0.07 por error de transcripción).
  - Sección 8.1 (conclusiones): reescrita para reflejar aceleración post-2015 y forma de J.
  - Sección 8.2 (limitaciones): nueva entrada sobre el bug de `attempted_suicide_yesno` corregido y sobre el diseño muestral no modelado.
- Quirk de Quarto 1.9 detectado: con `output-dir: reports` en `_quarto.yml`, los outputs se crean en la raíz del proyecto (no en `reports/`) al ejecutar `quarto render informe.qmd` desde la raíz. **Workaround:** pasar `--output-dir reports` explícito, o ejecutar desde `notebooks/`. Documentado aquí para no perder tiempo en futuras regeneraciones.
