# Wired Apart

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>
<a target="_blank" href="https://github.com/drivendata/cookiecutter-data-science">
    <img src="https://img.shields.io/badge/built%20with-uv-7F3FF2?logo=uv" />
</a>
<a target="blank" href="https://quarto.org">
    <img src="https://img.shields.io/badge/report-Quarto-74A0CF?logo=quarto" />
</a>
<a target="_blank" href="https://github.com/dahdor/wired-apart/actions">
    <img src="https://img.shields.io/badge/license-MIT-blue" />
</a>

> **Cuantificando el coste de la childhood digital sobre el bienestar adolescente (EE.UU., 2005–2021).**

---

## TL;DR

- **Pregunta.** ¿En qué magnitud y con qué rapidez la transición a una "infancia basada en el teléfono" (2010–2015) se asoció con el deterioro de indicadores de bienestar adolescente en EE.UU., y qué marco de monitoreo e intervención digital permite medir y revertir ese efecto en entornos escolares?
- **Método.** Replicación cuantitativa de los argumentos de *The Anxious Generation* (Haidt, 2024) integrando dos fuentes públicas: **CDC YRBS** (*Youth Risk Behavior Surveillance System*) —que combina en un mismo dataset la exposición (horas de pantalla) y los *outcomes* (depresión, ideación suicida) en adolescentes de 9°-12° grado— y **CDC NCHS WONDER / Socrata** (*Underlying Cause of Death*) —que provee las tasas de mortalidad por suicidio por edad/sexo/año—. Pipeline reproducible: limpieza con orden metodológico explícito (tipos → categorías → imposibles → faltantes), EDA, análisis de correlación segmentado, regresión logística ponderada, *trend tests*, y verificación de la Paradoja de Simpson.

  > **Nota sobre la elección de datasets.** El plan original contemplaba MTF + NSDUH. Ambos requieren registro en portales restringidos (ICPSR y SAMHSA) que no son automatizables desde un pipeline reproducible. YRBS y WONDER son las dos fuentes públicas equivalentes que **el libro también cita** (la Figura 1.4 sobre visitas a urgencias por autolesión usa datos de YRBS) y permiten construir exactamente la misma evidencia, con la ventaja adicional de que YRBS incluye la variable de exposición (tiempo de pantalla) directamente.

- **Hallazgos clave (estimaciones ponderadas, YRBS 2005-2021).**
  1. **sad/hopeless** en adolescentes subió de **28.5% (2005) a 42.3% (2021)** = **+48%** en 16 años.
  2. **Mujeres**: 36.7% → **56.6%** = **+54%**. **Hombres**: 20.4% → 28.6% = **+40%**. **Gap de género** creció de 16.4pp a **28.0pp** (amplificación del 71%).
  3. **Regresión logística** (n=131,936): OR de 2021 vs 2005 = **1.93** (IC95 1.84-2.03), controlando por sexo y edad.
  4. **Screen time 2019 (forma de J, no monotónica):** OR ajustados vs no-uso: 1.19 (<1h), 0.95 (1h), 1.14 (2h), 1.32 (3h), 1.85 (4h), **2.14 (5+h/día)**. Riesgo crece fuertemente a partir de 3h/día; uso de 1h tiene OR ligeramente *inferior* al no-uso (ver análisis 4 de `notebooks/3.0-dh-analysis.ipynb`).
  5. **Mortalidad 15-19** (NCHS Data Brief 471, agregado ambos sexos): 7.5/100k (2010) → 12.0/100k (2018) = **+60%**. Pico masculino 17.9/100k (HUS 2018 Table 9) en 2017.
  6. **Aceleración post-2015, no durante el rewiring:** los datos muestran una subida modesta 2010-2015 (+3.8pp en 6 años); el salto real es 2017→2021 (+10.8pp en 4 años). La ventana "rewiring" de Haidt no es un punto de inflexión en la serie.
  7. **Divorcio YRBS-NCHS:** las mujeres tienen 2x la depresión de los hombres pero 1/3 de su mortalidad completed. La mortalidad **no captura** la carga de salud mental femenina.
- **Propuesta.** Framework *Phone-Free Schools* con 4 palancas operacionales, 5 KPIs SMART con líneas base cuantificadas, y diseño A/B (RCT cluster-aleatorizado, n=3 000, 2 años, USD 210/est/año, ROI estimado 3-5x).

> El informe técnico completo (renderizado con Quarto) está en `reports/informe.html` y `reports/informe.pdf`.

---

## Estructura del repositorio

```
wired-apart/
├── README.md                 ← este archivo (con storytelling)
├── Makefile                  ← atajos: make install, make pipeline, make report
├── pyproject.toml            ← dependencias (gestionado con uv)
├── uv.lock                   ← versiones exactas (reproducibilidad)
├── informe.qmd               ← informe técnico en Quarto
├── _quarto.yml               ← configuración del proyecto Quarto
├── logo-unimet.png           ← logo para el front matter del informe
├── LICENSE                   ← MIT
│
├── data/                     ← versionado en disco local
│   ├── raw/                  ← datos crudos inmutables (NO se commitean a git)
│   ├── interim/              ← pasos intermedios (NO se commitean)
│   ├── processed/            ← datos limpios finales (commiteados: outputs reproducibles)
│   └── external/             ← PDFs de referencia (commiteados si < 5 MB)
│
├── notebooks/                ← Jupyter notebooks del pipeline (8)
│   ├── 0.0-dh-data-acquisition.ipynb    ← descarga YRBS 2005-2021 + Socrata
│   ├── 1.0-dh-yrbs-cleaning.ipynb       ← limpieza con crosswalk Q-codes
│   ├── 1.1-dh-wonder-cleaning.ipynb     ← combina Socrata + HUS 2018 Table 9
│   ├── 2.0-dh-eda-yrbs.ipynb            ← 5 figuras EDA (sad/hopeless, gap, screen time)
│   ├── 2.1-dh-eda-wonder.ipynb          ← 4 figuras EDA (mortalidad adolescente)
│   ├── 3.0-dh-analysis.ipynb            ← regresión, trend, Simpson (7 tests)
│   ├── 4.0-dh-storytelling.ipynb        ← 3 figuras adicionales (outliers, zoom-out, factores)
│   └── 5.0-dh-solution.ipynb            ← framework Phone-Free Schools
│
├── references/               ← data dictionaries y documentación de fuentes
│   ├── yrbs_data_dictionary.md           ← Q-codes + crosswalk
│   ├── wonder_data_dictionary.md         ← ICD-10 X60-X84, HUS 2018 Table 9
│   ├── data_provenance.md               ← hashes SHA-256 + URLs + cobertura
│   ├── references.bib                   ← BibTeX
│   └── apa.csl                          ← Citation Style Language
│
├── reports/                  ← entregables finales
│   ├── figures/              ← 13 figuras PNG narradas (fig1–fig13; fig10 = mortalidad vs depresión)
│   ├── informe.html          ← 5.7 MB, self-contained
│   ├── informe.pdf           ← 2.7 MB, 24 páginas
│   └── logo-unimet.png
│
├── wired_apart/              ← módulo Python de soporte
│   ├── config.py             ← rutas, paleta, ventana, constantes del rewiring
│   ├── dataset.py            ← loaders + YRBS_QCODE_CROSSWALK + sha256
│   ├── features.py           ← cohortes, períodos, tasas, zscore
│   └── plots.py              ← estilo + highlight_period + save
│
└── handoff.md                ← notas vivas del proyecto (contexto, quirks, decisiones)
```

---

## Cómo reproducir el análisis

El proyecto está diseñado para ser reproducible con un solo comando
después de instalar los requisitos listados abajo. El pipeline es
**idempotente**: re-ejecuciones producen los mismos outputs (mismo SHA256).

### Requisitos de software

- [Python 3.12](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias y entornos)
- [Quarto ≥ 1.9](https://quarto.org/docs/get-started/) (para el informe HTML/PDF)
- *(Opcional)* [`make`](https://www.gnu.org/software/make/) para los atajos. **No es requerido** — cada target tiene un equivalente directo en `uv run`.
- *(Solo Windows, opcional)* [Microsoft Access ODBC Driver](https://www.microsoft.com/en-us/download/details.aspx?id=54920) para la descarga inicial de YRBS. Si no, **el stacked raw parquet ya está commiteado** en `data/processed/yrbs_2005_2021.parquet` y puedes saltarte el notebook 0.0.
- **TinyTeX (LaTeX)** se instala automáticamente al ejecutar `make install` (vía `quarto install tinytex`). No requiere acción manual.

### Pasos con `make` (recomendado, todas las plataformas)

```bash
# 1. Clonar
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart

# 2. Instalar dependencias y crear el venv (incluye TinyTeX para el PDF)
make install

# 3. Ejecutar todo el pipeline (descarga + notebooks + informe + tests)
make validate
```

**En Windows**, `make install` + `make validate` son suficientes. No
necesitas el driver ODBC porque el stacked raw parquet está commiteado
y `validate_pipeline.py` salta automáticamente el notebook 0.0 en
plataformas no-Windows.

**En Linux/macOS**, lo mismo. El driver ODBC no se necesita: solo se
usa para regenerar el stacked raw desde los `.mdb` originales (notebook
0.0), pero ese output ya está commiteado.

Si prefieres no usar `make`, los mismos comandos funcionan con `uv` directamente:

```bash
# 1. Clonar
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart

# 2. Instalar dependencias
uv sync --all-extras

# 3. Pipeline + render (notebooks 1.0–5.0, luego Quarto HTML+PDF)
uv run python scripts/validate_pipeline.py --skip-download
```

**Notas para Windows:**
- `make` no viene preinstalado; instalalo con [Chocolatey](https://chocolatey.org/install) (`choco install make`) o usa los comandos `uv` de arriba.
- Git Bash o PowerShell funcionan; los comandos son portables.
- `jupyter nbconvert --execute --inplace` es el método correcto para ejecutar notebooks en Windows (no usar `jupyter execute`, que tiene bugs conocidos en Windows).

### Targets de `make` disponibles

| Target | Qué hace |
|---|---|
| `make install` | `uv sync --all-extras` + `quarto install tinytex` |
| `make test` | 38 tests pytest (integridad, anti-regresión, heatmap) |
| `make pipeline` | Ejecuta los 8 notebooks en orden (skip 0.0 en Linux/macOS) |
| `make report` | Renderiza el informe a HTML y PDF |
| `make validate` | download + pipeline + report + tests + check outputs |
| `make validate-no-pdf` | Igual a `validate` pero **sin PDF** (HTML sí, TinyTeX no) |
| `make validate-quick` | Solo tests + verificación de outputs (no re-ejecuta) |
| `make download` | Descarga YRBS .mdb + NCHS Socrata (idempotente, skip ODBC en Linux) |
| `make clean` | Borra pyc, __pycache__, .ipynb_checkpoints |
| `make lint` / `format` | ruff check / auto-format |

`make validate` acepta `EXTRA="..."` para pasar flags al script subyacente:
```bash
make validate EXTRA="--skip-pdf"          # HTML only, no TinyTeX
make validate EXTRA="--install-tinytex"   # fuerza TinyTeX (pese a tener MiKTeX/TeX Live)
```

### Sobre el render PDF y LaTeX

El informe en PDF requiere un motor LaTeX. El script detecta automáticamente
si el sistema tiene uno disponible y solo descarga TinyTeX si es necesario:

| Sistema | Comportamiento por defecto |
|---|---|
| Linux/macOS con TeX Live / MacTeX | Usa el motor del sistema. **No descarga TinyTeX.** |
| Windows con MiKTeX | Usa el motor del sistema (típicamente `lualatex`). **No descarga TinyTeX.** |
| Cualquier sistema SIN LaTeX | Instala TinyTeX (~1 GB, varios minutos con progreso visible). |
| `make validate-no-pdf` o `EXTRA="--skip-pdf"` | Saltea PDF y TinyTeX por completo. |

Si querés forzar la instalación de TinyTeX aunque tengas LaTeX (por ejemplo,
para pinear la versión en CI), usá `make validate EXTRA="--install-tinytex"`.

### Solo regenerar el informe (sin re-ejecutar notebooks)

```bash
# Con make
make report

# Sin make
uv run quarto render informe.qmd --to html
uv run quarto render informe.qmd --to pdf
```

Los outputs se guardan en `reports/informe.html` y `reports/informe.pdf`.

---

## Reproducibilidad

El proyecto está diseñado para que un clon fresco pueda regenerar **todos** los outputs (datos limpios, figuras, informe HTML+PDF) sin intervención manual.

### Flujo recomendado (cualquier plataforma)

```bash
# Clonar, instalar, ejecutar pipeline, renderizar, validar.
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart
make install      # uv sync --all-extras + quarto install tinytex
make validate     # pipeline + report + tests (skip-download si ya tienes los datos)
```

### Componentes de reproducibilidad

| Componente | Ubicación | Propósito |
|---|---|---|
| **`uv.lock`** | raíz | Versiones exactas de todas las dependencias (145 paquetes). |
| **`scripts/download_data.py`** | scripts/ | Descarga YRBS .mdb + NCHS Socrata, verifica SHA-256. Idempotente. |
| **`scripts/validate_pipeline.py`** | scripts/ | Ejecuta download → pipeline → report → tests → check outputs. Detecta plataforma para saltar pasos Windows-only. |
| **`scripts/fix_attempted_suicide.py`** | scripts/ | Reproduce la corrección del bug de `attempted_suicide_yesno` (CHANGELOG #1) sin ODBC. |
| **`scripts/fix_hispanic_yesno.py`** | scripts/ | Reproduce la corrección del bug de `hispanic_yesno` 2005 (CHANGELOG #21) sin ODBC. |
| **`tests/`** | tests/ | 32 tests pytest: integridad de schema, codificación, anti-regresión de headlines, funciones puras, anti-regresión de los 4 fixes de la auditoría jun-2026. |
| **`.github/workflows/ci.yml`** | .github/workflows/ | CI en Linux y Windows: ejecuta `validate_pipeline.py` end-to-end, sube HTML y PDF como artifacts. |
| **`CHANGELOG.md`** | raíz | Historial de correcciones con impacto y archivos modificados. |
| **`references/data_provenance.md`** | references/ | SHA-256 de cada archivo crudo YRBS + URLs + cobertura. |
| **`data/processed/yrbs_2005_2021.parquet`** | data/processed/ | Stacked raw commiteado (6.2 MB). Permite correr notebooks 1.0–5.0 sin ODBC. |
| **`data/external/*.pdf`** | data/external/ | PDFs de referencia (NCHS HUS 2018 Table 9, DB 471) commiteados. |

### Garantías

- **Determinismo:** seeds explícitos en `config.RANDOM_SEED`; los notebooks no usan procesos estocásticos reales (todas las estadísticas son ponderadas o deterministas).
- **Idempotencia:** los notebooks de cleaning (1.0, 1.1) producen el mismo SHA256 en re-runs sucesivos. `download_data.py` y `validate_pipeline.py` pueden correr múltiples veces sin side effects.
- **Auditabilidad:** 32 tests pytest detectan cambios accidentales (incluyendo los 4 fixes críticos de la auditoría jun-2026: `hispanic_yesno` 2005, Simpson ponderado, OR/χ² consistente, CA cluster-robust).
- **Plataforma:** CI corre en Linux y Windows; el script `validate_pipeline.py` detecta la plataforma y salta el notebook 0.0 (Windows-only) automáticamente.

### Limitaciones honestas de la reproducibilidad

- **Notebook 0.0 (adquisición YRBS .mdb) solo corre en Windows con Microsoft Access ODBC.** En otras plataformas, los `.mdb` se descargan pero no se pueden convertir a Parquet. **No es bloqueante:** el stacked raw parquet commiteado (`data/processed/yrbs_2005_2021.parquet`, 6.2 MB) permite ejecutar todo el pipeline sin esa dependencia. Si necesitás regenerar el stacked raw, hacelo una vez en Windows y commitea el resultado.
- **NCHS HUS 2018 Table 9:** los 12 valores (2010, 2016, 2017) están hardcodeados en el notebook 1.1. El PDF original está commiteado en `data/external/`. Si los valores oficiales cambian, hay que actualizar manualmente el notebook.
- **NCHS Data Brief 471:** la cifra "7.5/100k (2010) → 12.0/100k (2018)" es lectura humana del PDF, no se computa del pipeline automatizado.
- **Quarto 1.9 quirk:** con `output-dir: reports` en `_quarto.yml`, los outputs a veces se crean en la raíz. Workaround: pasar `--output-dir reports` explícito (lo hace el script `validate_pipeline.py`).

---

## Datos utilizados

| Dataset | Fuente | Unidad | Ventana efectiva | n | Variables clave |
|---|---|---|---|---|---|
| **CDC YRBS** (National High School YRBS) | [CDC YRBS](https://www.cdc.gov/yrbs/data/index.html) | Individual (~13-17 k / año, 9°-12° grado) | **9 olas bianuales: 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021** | 134 674 total | sad/hopeless, considered/made_plan/attempted suicide, screen time (Q80 2019 only), weight, stratum, psu, race (CDC `raceeth`), hispanic |
| **CDC NCHS Socrata** (suicide rates) | [data.cdc.gov w26f-tf3h](https://data.cdc.gov/NCHS/NCHS---Death-rates-from-suicide/w26f-tf3h) | Agregado (tasas por 100k + IC95%) | 2018–2024 (7 años) | 28 filas (4 grupos × 7 años) | Tasa cruda por sexo (M/F) y grupo de edad (10-14, 15-19) |
| **NCHS HUS 2018 Table 9** (PDF) | [NCHS HUS 2018](https://www.cdc.gov/nchs/hus) | Tabla PDF (tasas crudas) | 2010, 2016, 2017 (3 años) | 12 filas (4 grupos × 3 años) | Misma granularidad que Socrata |
| **NCHS Data Brief 471** (PDF) | [db471.pdf](https://www.cdc.gov/nchs/data/databriefs/db471.pdf) | Referencia cualitativa | 2000-2021 | — | Mortalidad 15-19 agregada (ambos sexos), Figura 1 |

**Por qué estos dos.** YRBS combina la **exposición** (horas de pantalla) con los **outcomes** (depresión, suicidios intentados) en la misma unidad de análisis (el adolescente), permitiendo asociación a nivel individual. WONDER provee los **outcomes de mortalidad** (suicidios consumados) que YRBS no captura porque su población es solo high school. Juntos permiten responder la pregunta de investigación en dos niveles: asociación individual (YRBS) y tendencia poblacional agregada (WONDER/NCHS).

**Limitaciones reportadas de los datos.**

- **YRBS es bienal** (años impares). Para años pares no hay datos; los gráficos temporales se interpolan visualmente con líneas punteadas.
- **YRBS excluye adolescentes no escolarizados** (dropouts, homeschoolers), que tienen mayor prevalencia de depresión y suicidio. Esto subestima la prevalencia real.
- **Q80 (screen time) solo es válido en 2019.** En otros años, Q80 mide actividad física, TV, o deportes. Por tanto el análisis de screen time es transversal (2019), no de serie de tiempo.
- **CDC WONDER API caída en este entorno:** D76, D77, D158, D176 devuelven HTTP 400 a toda query programática. Workaround: Socrata 2018-2024 + HUS 2018 Table 9 (3 años extra: 2010, 2016, 2017). **Gaps documentados: 2005-2009 y 2011-2015.**
- **Q-codes rotan cada 2 años** (mismo concepto, número de pregunta cambia). El crosswalk validado está en `references/yrbs_data_dictionary.md` y `wired_apart/dataset.py`.
- **Los datos son de EE.UU.** La transferibilidad a otros contextos (incluido Venezuela) se discute en el informe; no se asume.

---

## Hallazgos detallados

> Cifras ponderadas por `weight` salvo donde se indique. Ver `notebooks/3.0-dh-analysis.ipynb` para los detalles estadísticos.

### 1. Tendencia global: sad/hopeless 2005-2021

- **28.5% (2005) → 42.3% (2021) = +13.8pp (+48%)** en 16 años.
- Test de tendencia (jun-2026, survey-weighted logistic regression con SE
  cluster-robust en PSU): log-OR/año mujeres = +0.0471 (z=12.4, p<0.001);
  hombres = +0.0269 (z=8.7, p<0.001). OR acumulada 2005→2021: **2.13 mujeres
  (IC95 1.89-2.39) y 1.54 hombres (IC95 1.40-1.70)**. Pendiente en pp/año
  (delta-method): ~+1.14 mujeres, ~+0.47 hombres. *Nota:* el log-OR/año
  resume la tendencia media en la escala log-odds; los datos son no
  lineales (aceleración post-2015).
- Aceleración post-2015: 2017-2021 aporta +10.8pp de los 13.8pp totales.

### 2. Asimetría de género amplificándose (LA CIFRA CLAVE)

| Año | Mujeres | Hombres | Gap F-M |
|---|---|---|---|
| 2005 | 36.7% | 20.4% | +16.4pp |
| 2009 | 33.9% | 19.1% | +14.8pp |
| 2013 | 39.1% | 20.8% | +18.3pp |
| 2017 | 41.1% | 21.4% | +19.7pp |
| 2019 | 46.6% | 26.8% | +19.9pp |
| **2021** | **56.6%** | **28.6%** | **+28.0pp** |

**Lectura:** el gap de género creció de 16.4pp a 28.0pp (×1.7). **Para 2021, más de la mitad (56.6%) de las mujeres adolescentes reportan sad/hopeless 2+ semanas seguidas.** Consistente con la hipótesis de Haidt sobre plataformas *image-based* que afectan desproporcionadamente a mujeres.

### 3. Dosis-respuesta con screen time (2019) — **forma de J, no monotónica**

| Screen time (h/día) | OR ajustado (IC95) | % sad/hopeless ponderado |
|---|---|---|
| 0 (no usa) | 1.00 (referencia) | 33.5% |
| <1h | 1.19 (1.03-1.38) | 33.0% |
| **1h** | **0.95 (0.81-1.10)** | **28.1%** |
| 2h | 1.14 (1.00-1.30) | 31.9% |
| 3h | 1.32 (1.16-1.51) | 35.2% |
| 4h | 1.85 (1.60-2.13) | 43.7% |
| **5+h** | **2.14 (1.90-2.41)** | **47.8%** |

La curva es **decreciente para 0–1h y luego creciente**, no monotónica. El mínimo de riesgo se observa en 1h/día (OR < 1), y el riesgo se acelera a partir de 3h/día. Esto es consistente con la hipótesis de Haidt (uso problemático encolas en horas altas) pero **invalida una lectura lineal**. **Caveat:** transversal, no longitudinal; causalidad inversa posible.

### 4. Mortalidad adolescente (NCHS)

- **Pico masculino 15-19:** 17.9/100k (2017, HUS), bajando a 13.3/100k (2024, Socrata).
- **Mortalidad femenina 15-19** más estable: 3.1/100k (2010, HUS) → 5.4/100k (2024, Socrata) = +74%.
- **Ratio M/F** en 15-19 cayó de 3.78x (2010) a 2.46x (2024) = -35% (feminización del riesgo).
- **Agregado ambos sexos** (NCHS DB 471): 7.5/100k (2010) → 12.0/100k (2018) = +60%.

### 5. Pre/post Great Rewiring (chi-cuadrado)

- Pre (2005-2009): 27.6% sad/hopeless, n=43,811.
- Post (2017-2021): 37.1% sad/hopeless, n=45,003.
- Diferencia: **+8.6pp**, Wald χ²=141.6, p<0.001, **OR=1.48 (IC95 1.39-1.58)**
  (jun-2026, regresión logística ponderada con SE cluster-robust en PSU;
  DEFF=2.69, es decir, el diseño muestral infla el SE en ~170% respecto
  al IID).

### 6. Paradoja de Simpson

Estratificación por sexo × raza (8 categorías CDC, válida 2007+). **No hay inversión**, pero sí heterogeneidad real:

- **Mujeres suben en todas las razas** (+6.7 a +14.4pp).
- **Hombres más heterogéneos:** hispanos (-0.3pp) y NHPI (-4.8pp) se mantienen o bajan; blancos y nativos suben.

---

## Solución propuesta: Framework *Phone-Free Schools*

**4 palancas operacionales** (vinculadas a evidencia cuantitativa):

1. **Recoger** — Lockers magnéticos en la entrada. Reduce exposición 5+h/día → <1h/día. Basado en OR 2.14 (5+h) vs 1.19 (<1h) en 2019. Costo: $50/est/año.
2. **Reemplazar** — Recreo estructurado (deportes, lectura, club). Llena el vacío de atención. Costo: $100/est/año.
3. **Monitorear** — Encuesta bienestar semestral (PHQ-5 adaptado). Mide morbilidad sentida, no solo mortalidad. Costo: $20/est/año.
4. **Capacitar** — Talleres a profesores (signos de alerta, primeros auxilios emocionales). Costo: $30/est/año.

**Costo total:** ~$210/estudiante/año (1.4% del per cápita K-12 en USA, ~$15,000/est/año).

**ROI estimado:** 3-5x en costos evitados de salud mental (Lee et al. 2022, *Lancet Child & Adolescent Health*).

**5 KPIs SMART con líneas base cuantificadas:**

| KPI | Baseline | Meta | Plazo |
|---|---|---|---|
| sad/hopeless overall | **42.3% (2021)** | 33% | 2 años |
| sad/hopeless mujeres | **56.6% (2021)** | 45% | 2 años |
| screen time 5+h/día | 25% (2019) | 10% | 1 año |
| mortalidad 15-19 | 6/100k | ≤6/100k | 5 años |
| cyberbullying | 15% (2021) | 10% | 2 años |

**Diseño de evaluación:** RCT cluster-aleatorizado (30 escuelas treatment + 30 control en el mismo distrito), n≈3 000, 2 años académicos, análisis diferencia-en-diferencias con efectos fijos de escuela y tendencia temporal.

---

## Limitaciones metodológicas

1. **Evidencia asociativa, no causal estricta.** El RCT propuesto es lo que daría causalidad. Mientras tanto, hay causalidad inversa posible (adolescentes deprimidos usan más pantallas).
2. **Cohorte acotada.** YRBS es high school (9°-12°). Los pre-adolescentes (10-13) están subrepresentados. YRBS excluye dropouts y homeschoolers, que probablemente tienen mayor prevalencia.
3. **Screen time cross-sectional.** Solo 2019 captura la métrica de Haidt (social media + video + games). Los demás años miden TV, deportes, o actividad física.
4. **Mortalidad gaps 2005-2009 y 2011-2015.** WONDER API caída. Workaround con HUS 2018 Table 9 (3 años). Datos leídos manualmente del PDF.
5. **Alcance escolar del framework.** El phone-free cubre 7h/día, no las 17h restantes. Decisiones de hogar son de los padres.
6. **Reporte de eventos sensibles** (suicidio, screen time) en encuestas escolares está sujeto a desirability bias y subreporte.
7. **PHQ-5 autoreportado** puede tener desirability bias post-intervención (los estudiantes saben que el programa usa la encuesta).
8. **Generalización cultural.** Contexto USA 2010-2021; transferibilidad a otros países no se asume.
9. **Diseño muestral complejo — ahora modelado en los análisis 2 y 5 (jun-2026).** Las regresiones de tendencia (análisis 2) y pre/post (análisis 5) usan **errores cluster-robust agrupados por PSU** (`cov_type='cluster'`), lo que corrige la subestimación de SE que existía al usar solo `freq_weights`. El DEFF ≈ 2.7, es decir, el SE cluster-robust es ~170% del SE IID. Los IC95 son más anchos y honestos. **Pendientes:** los análisis 3 (regresión logística con año+sexo+edad) y 4 (regresión screen time 2019) todavía usan `freq_weights` sin cluster-robust. Quedan como trabajo futuro, pero no afectan el headline (las conclusiones direccionales son robustas).
10. **Simpson reescrito con medias ponderadas + bootstrap CIs (jun-2026).** La versión previa usaba medias no ponderadas, lo que invertía el signo en 3 celdas (F-NHPI, M-Hispanic, M-Multi) y producía una narrativa falsa de "excepciones protectoras" en hombres. La nueva versión usa proporciones ponderadas y bootstrap CIs; las "excepciones" se debilitan (los cambios no son significativamente distintos de 0 pero tampoco outliers negativos). Celdas con n_pre < 200 (F-AmIndian, F-NHPI, M-NHPI) se marcan con `*` en el heatmap.

---

## Resultados verificables

Para quien quiera auditar los números:

```bash
# Ejecutar el pipeline (5-10 min end-to-end)
make pipeline

# El notebook 3.0 imprime las tablas de regresión, OR, chi², p-valores.
# Las cifras ponderadas se validan contra la oficial: 2019 sad/hopeless = 36.7%
# (mismo valor que reporta el CDC en su YRBS Data Summary & Trends Report).
```

Outputs:
- `data/processed/yrbs_clean_2005_2021.parquet` — 134,674 × 17 (cleaned YRBS).
- `data/processed/wonder_clean_2005_2024.csv` — 40 × 9 (cleaned NCHS mortalidad).
- `reports/figures/fig[1-13]_*.png` — 13 figuras narradas (fig10 = mortalidad vs depresión; nota: el README mencionaba "14" por error, ver CHANGELOG.md).
- `reports/informe.html` (5.7 MB), `reports/informe.pdf` (2.7 MB, 24 p).

---

## Documentación adicional

Todo lo que se necesita para entender el proyecto está en este repositorio.

- **Notas vivas (handoff):** `handoff.md` en este directorio. Contiene contexto, decisiones, quirks de herramientas, y lista de bugs corregidos en la revisión de jun-2026.
- **Data dictionaries:**
  - `references/yrbs_data_dictionary.md` — Q-codes, crosswalk, Q80 solo 2019, race=CDC `raceeth`.
  - `references/wonder_data_dictionary.md` — ICD-10 X60-X84, HUS 2018 Table 9.
  - `references/data_provenance.md` — hashes SHA-256, URLs, cobertura.
- **Bibliografía:** `references/references.bib` (BibTeX con Haidt 2024, Twenge 2017, Dawson 2020, CDC, NCHS, Lee 2022).
- **Estilo CSL:** `references/apa.csl` (Citation Style Language APA 7).

---

## Autor y contexto académico

- **Autor:** Diego Hernández — C.I. 31.045.867
- **Materia:** Análisis de Datos — FPTSP27 — Sección 1
- **Institución:** Universidad Metropolitana — Facultad de Ingeniería — Departamento de Gestión de Proyectos y Sistemas
- **Período académico:** 2526-3 (tercer trimestre 2025-2026)

---

## Licencia

MIT — ver [`LICENSE`](LICENSE).
