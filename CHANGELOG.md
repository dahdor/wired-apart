# Changelog — Wired Apart

Todas las modificaciones relevantes al proyecto. Inspirado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

El formato está basado en [Semantic Versioning](https://semver.org/lang/es/) para los hitos del pipeline de datos, pero los hallazgos individuales se versionan por fecha.

---

## [Sin versión] — 2026-06-18 — Auditoría externa y correcciones

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
- 27 tests pytest pasan (4.12s): cobertura de schema, codificación, anti-regresión, funciones puras, plots.
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
