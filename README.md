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
  4. **Screen time 2019 (dosis-respuesta):** OR ajustados de 0.95 (1h), 1.14 (2h), 1.32 (3h), 1.85 (4h), **2.14 (5+h/día)** vs no-uso.
  5. **Mortalidad 15-19** (NCHS Data Brief 471, agregado ambos sexos): 7.5/100k (2010) → 12.0/100k (2018) = **+60%**. Pico masculino 17.9/100k (HUS 2018 Table 9) en 2017.
  6. **Cambio de régimen 2010-2015** coincide con la ventana del Great Rewiring teorizado por Haidt.
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
│   ├── figures/              ← 14 figuras PNG narradas
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

### Requisitos

- [Python 3.12](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias y entornos)
- [Quarto ≥ 1.9](https://quarto.org/docs/get-started/) (para el informe)
- [TeX](https://quarto.org/docs/output-formats/pdf-basics.html) o [Typst](https://quarto.org/docs/output-formats/pdf-basics.html) (para el PDF)
- Microsoft Access ODBC Driver (Windows, para la descarga inicial de YRBS) o pre-colocar los `.mdb` en `data/raw/yrbs/`
- *(Opcional)* [`make`](https://www.gnu.org/software/make/) para los atajos. **No es requerido** — cada target tiene un equivalente directo en `uv run`.

### Pasos con `make` (recomendado)

```bash
# 1. Clonar
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart

# 2. Instalar dependencias y crear el venv
make install

# 3. Colocar los datos crudos en data/raw/yrbs/  (ver references/data_provenance.md)
#    Si no los tenés, notebook 0.0 los descarga automáticamente desde CDC.

# 4. Ejecutar todo el pipeline (5-10 min end-to-end)
make all           # equivalente a: make pipeline && make report

# O paso a paso:
make pipeline      # ejecuta los 8 notebooks en orden
make report        # renderiza el informe a HTML y PDF
make clean         # borra pyc, __pycache__, .ipynb_checkpoints
make lint          # ruff check + format check
make format        # auto-format con ruff
```

### Pasos sin `make` (equivalentes portables para Windows/macOS)

`make` no viene preinstalado en Windows ni en macOS. Si no lo tenés, los mismos comandos funcionan con `uv` directamente:

```bash
# 1. Clonar
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart

# 2. Instalar dependencias
uv sync --all-extras

# 3. Pipeline: ejecutar cada notebook end-to-end
# IMPORTANTE: usar nbconvert --execute --inplace (no `jupyter execute` que
# no guarda outputs en Windows).
for nb in notebooks/*.ipynb; do
  uv run jupyter nbconvert --to notebook --execute --inplace "$nb"
done

# 4. Renderizar el informe (HTML y PDF)
uv run quarto render informe.qmd --to html
uv run quarto render informe.qmd --to pdf
```

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
- Cochran-Armitage trend test: pendiente mujeres +1.09pp/año (p<0.001); hombres +0.44pp/año (p<0.001).
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

### 3. Dosis-respuesta con screen time (2019)

| Screen time (h/día) | OR ajustado (IC95) |
|---|---|
| <1h | 1.19 (1.03-1.38) |
| 1h | 0.95 (0.81-1.10) |
| 2h | 1.14 (1.00-1.30) |
| 3h | 1.32 (1.16-1.51) |
| 4h | 1.85 (1.60-2.13) |
| **5+h** | **2.14 (1.90-2.41)** |

Asociación monotónica, estadísticamente significativa. **Caveat:** transversal, no longitudinal; causalidad inversa posible.

### 4. Mortalidad adolescente (NCHS)

- **Pico masculino 15-19:** 17.9/100k (2017, HUS), bajando a 13.3/100k (2024, Socrata).
- **Mortalidad femenina 15-19** más estable: 3.1/100k (2010, HUS) → 5.4/100k (2024, Socrata) = +74%.
- **Ratio M/F** en 15-19 cayó de 3.78x (2010) a 2.46x (2024) = -35% (feminización del riesgo).
- **Agregado ambos sexos** (NCHS DB 471): 7.5/100k (2010) → 12.0/100k (2018) = +60%.

### 5. Pre/post Great Rewiring (chi-cuadrado)

- Pre (2005-2009): 27.6% sad/hopeless, n=43,811.
- Post (2017-2021): 37.1% sad/hopeless, n=45,003.
- Diferencia: **+9.5pp**, χ²=919, p<0.001, OR=1.55.

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
- `reports/figures/fig[1-14]_*.png` — 14 figuras narradas.
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
