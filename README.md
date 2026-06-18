# Wired Apart

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>
<a target="_blank" href="https://github.com/drivendata/cookiecutter-data-science">
    <img src="https://img.shields.io/badge/built%20with-uv-7F3FF2?logo=uv" />
</a>
<a target="_blank" href="https://quarto.org">
    <img src="https://img.shields.io/badge/report-Quarto-74A0CF?logo=quarto" />
</a>

> **Cuantificando el coste de la childhood digital sobre el bienestar adolescente (EE.UU., 2005–2020).**

---

## TL;DR

- **Pregunta.** ¿En qué magnitud y con qué rapidez la transición a una "infancia basada en el teléfono" (2010–2015) se asocia con el deterioro de indicadores de bienestar adolescente en EE.UU., y qué marco de monitoreo e intervención digital permite medir y revertir ese efecto en entornos escolares?
- **Método.** Replicación cuantitativa de los argumentos de *The Anxious Generation* (Haidt, 2024) integrando dos fuentes públicas: **CDC YRBS (Youth Risk Behavior Surveillance System)** —que combina en un solo dataset la exposición (horas de pantalla) y los outcomes (depresión, ideación suicida) en adolescentes de 9°-12° grado— y **CDC WONDER (Underlying Cause of Death)** —que provee las tasas de mortalidad por suicidio por edad/sexo/año—. Pipeline: limpieza con orden metodológico explícito (tipos → categorías → imposibles → faltantes), EDA, análisis de correlación segmentado, y verificación de la paradoja de Simpson.

  > **Nota sobre la elección de datasets.** El plan original contemplaba MTF + NSDUH. Ambos requieren registro en portales restringidos (ICPSR y SAMHSA) que no son automatizables desde un pipeline reproducible. YRBS y WONDER son las dos fuentes públicas equivalentes que **el libro también cita** (la Figura 1.4 sobre visitas a urgencias por autolesión usa datos de YRBS) y permiten construir exactamente la misma evidencia, con la ventaja adicional de que YRBS incluye la variable de exposición (tiempo de pantalla) directamente.
- **Hallazgos clave.** (se completan al final del análisis).
- **Propuesta.** Framework de monitoreo *Phone-Free Schools* con métricas de proceso y resultado.

> El informe técnico completo (renderizado con Quarto) está en `reports/informe.html` y `reports/informe.pdf`.

---

## Estructura del repositorio

```
wired-apart/
├── README.md                 ← este archivo (con storytelling)
├── Makefile                  ← atajos: make install, make pipeline, make report
├── pyproject.toml            ← dependencias, gestionado con uv
├── uv.lock                   ← versiones exactas (reproducibilidad)
├── informe.qmd               ← informe técnico en Quarto
├── _quarto.yml               ← configuración del proyecto Quarto
├── logo-unimet.png           ← logo para el front matter del informe
│
├── data/                     ← todo versionado en disco local
│   ├── raw/                  ← datos crudos inmutables (NO se commitean a git)
│   ├── interim/              ← pasos intermedios de limpieza (NO se commitean)
│   ├── processed/            ← datos limpios finales (NO se commitean si son grandes)
│   └── external/             ← datos de terceros sin tocar (NO se commitean)
│
├── notebooks/                ← Jupyter notebooks del pipeline (8 en total)
│   ├── 0.0-dh-data-acquisition.ipynb
│   ├── 1.0-dh-mtf-cleaning.ipynb
│   ├── 1.1-dh-nsduh-cleaning.ipynb
│   ├── 2.0-dh-eda-mtf.ipynb
│   ├── 2.1-dh-eda-nsduh.ipynb
│   ├── 3.0-dh-analysis.ipynb
│   ├── 4.0-dh-storytelling.ipynb
│   └── 5.0-dh-solution.ipynb
│
├── references/               ← data dictionaries y documentación de fuentes
│   ├── mtf_data_dictionary.md
│   ├── nsduh_data_dictionary.md
│   └── data_provenance.md    ← hashes SHA-256, fechas de descarga, URLs
│
├── reports/                  ← entregables finales
│   ├── figures/              ← PNG/SVG de alta resolución
│   ├── informe.html
│   └── informe.pdf
│
└── wired_apart/              ← módulo Python de soporte
    ├── config.py             ← rutas, paleta, constantes
    ├── dataset.py            ← carga de YRBS y WONDER
    ├── features.py           ← cohortes, períodos, tasas
    └── plots.py              ← estilo consistente + helper de narrativa
```

---

## Cómo reproducir el análisis

### Requisitos
- [Python 3.12](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias y entornos)
- [Quarto ≥ 1.9](https://quarto.org/docs/get-started/) (para el informe)
- [TeX](https://quarto.org/docs/output-formats/pdf-basics.html) o [Typst](https://quarto.org/docs/output-formats/pdf-basics.html) (para el PDF)
- *(Opcional)* [`make`](https://www.gnu.org/software/make/) para los atajos. **No es requerido** — cada target tiene un equivalente directo en `uv run`.

### Pasos con `make` (recomendado)

```bash
# 1. Clonar
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart

# 2. Instalar dependencias y crear el venv
make install

# 3. Colocar los datos crudos en data/raw/  (ver references/data_provenance.md)
#    YRBS en data/raw/yrbs/  y WONDER en data/raw/cdc/

# 4. Ejecutar todo el pipeline
make all           # equivalente a: make pipeline && make report

# O paso a paso:
make pipeline      # ejecuta los 8 notebooks en orden
make report        # renderiza el informe a HTML y PDF
make test          # corre los tests de pytest
make clean         # borra pyc, __pycache__, .ipynb_checkpoints
```

### Pasos sin `make` (equivalentes portables)

`make` no viene preinstalado en Windows ni en macOS. Si no lo tenés, los mismos comandos funcionan directamente con `uv`:

```bash
# 1. Clonar
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart

# 2. Instalar dependencias
uv sync --all-extras

# 3. Colocar los datos crudos en data/raw/

# 4. Pipeline + informe
uv run python -m jupyter execute notebooks/0.0-dh-data-acquisition.ipynb
uv run python -m jupyter execute notebooks/1.0-dh-yrbs-cleaning.ipynb
# ... (repetir para cada notebook 1.x a 5.0)
uv run quarto render informe.qmd --to html
uv run quarto render informe.qmd --to pdf
```

O usar el script `scripts/run_pipeline.py` que encapsula la secuencia (lo agregamos en la Fase 7 si te parece útil).

### Solo regenerar el informe

```bash
# Con make
make report

# Sin make
uv run quarto render informe.qmd --to html
uv run quarto render informe.qmd --to pdf
```

---

## Datos utilizados

| Dataset | Fuente | Unidad | Ventana | n (aprox.) | Variables clave |
|---|---|---|---|---|---|
| **CDC YRBS** (National High School) | Centers for Disease Control and Prevention | Individual (~13 000 / año, 9°-12° grado) | 2005–2019 (años impares) | ~13 000 / año | Tiempo de pantalla (Q80), tristeza/sin esperanza (Q25), ideación suicida (Q26-28), peso/estatura, etnia, grado |
| **CDC WONDER** (Underlying Cause of Death) | Centers for Disease Control and Prevention | Agregado (conteos + tasas por 100k) | 1999–2020 | Cobertura nacional completa | Tasas de suicidio por edad (10-14, 15-19), sexo y año, ICD-10 X60-X84 |

**Por qué estos dos.** YRBS es un survey que combina la **exposición** (horas de pantalla/social media) con los **outcomes** (depresión, suicidios intentados) en la misma unidad de análisis (el adolescente), permitiendo análisis a nivel individual. WONDER provee los outcomes de **mortalidad** (suicidios consumados) que YRBS no captura porque su población es solo high school. Juntos permiten responder la pregunta de investigación en dos niveles: asociación individual (YRBS) y tendencia poblacional agregada (WONDER).

**Limitaciones reportadas.**
- YRBS es bienal (años impares: 2005, 2007, ..., 2019). Para años pares no hay datos; los gráficos temporales se interpolan visualmente con líneas punteadas.
- YRBS excluye adolescentes no escolarizados (mayor riesgo de depresión). Esto subestima la prevalencia real.
- Los datos son de EE.UU. La transferibilidad a otros contextos (incluido Venezuela) se discute en el informe, no se asume.

---

## Hallazgos clave (preview)

> _Esta sección se completa al final del análisis (Fase 6)._

1. **Hallazgo 1.** ...
2. **Hallazgo 2.** ...
3. **Hallazgo 3.** ...

---

## Solución propuesta: Framework de Monitoreo *Phone-Free Schools*

> _Esta sección se completa al final del análisis (Fase 7)._

Resumen de la propuesta en 3 bullets, vinculado a hallazgos específicos.

---

## Limitaciones generales

- Datos agregados y de corte transversal por año; no se pueden hacer claims causales estrictos.
- La ventana termina en 2020, lo que evita contaminar el análisis con la "Gran Disrupción" post-COVID pero también deja fuera la dinámica reciente.
- La "Gran Reconexión" (2010-2015) coincide con otros eventos (recesión tardía, polarización política). Se argumentan controles en el informe.

---

## Autor y contexto académico

- **Autor:** Diego Hernández — C.I. 31.045.867
- **Materia:** Análisis de Datos — FPTSP27 — Sección 1
- **Institución:** Universidad Metropolitana — Facultad de Ingeniería — Departamento de Gestión y Proyectos de Sistemas
- **Período:** 2526-2

---

## Licencia

MIT — ver [`LICENSE`](LICENSE).
