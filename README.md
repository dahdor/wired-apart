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
- **Método.** Replicación cuantitativa de los argumentos de *The Anxious Generation* (Haidt, 2024) integrando dos fuentes públicas: **Monitoring the Future (MTF)** —actitudes y conductas— y **National Survey on Drug Use and Health (NSDUH)** —diagnósticos clínicos—. Pipeline: limpieza con orden metodológico explícito (tipos → categorías → imposibles → faltantes), EDA, análisis de correlación segmentado, y verificación de la paradoja de Simpson.
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
    ├── dataset.py            ← carga de MTF y NSDUH
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

### Pasos

```bash
# 1. Clonar
git clone https://github.com/dahdor/wired-apart.git
cd wired-apart

# 2. Instalar dependencias y crear el venv
make install

# 3. Colocar los datos crudos en data/raw/  (ver references/data_provenance.md)
#    MTF en data/raw/mtf/  y NSDUH en data/raw/nsduh/

# 4. Ejecutar todo el pipeline
make all           # equivalente a: make pipeline && make report

# O paso a paso:
make pipeline      # ejecuta los 8 notebooks en orden
make report        # renderiza el informe a HTML y PDF
make test          # corre los tests de pytest
```

### Solo regenerar el informe

```bash
make report
```

---

## Datos utilizados

| Dataset | Fuente | Unidad | Ventana | n (aprox.) | Variables clave |
|---|---|---|---|---|---|
| **Monitoring the Future (MTF)** | Universidad de Michigan / NIDA | Individual (8°, 10°, 12° grado) | 2005–2020 | ~15 000 / año | Satisfacción con uno mismo, soledad, horas de sueño, "casi a diario" con amigos |
| **NSDUH** | SAMHSA | Individual (12+) | 2005–2020 | ~70 000 / año | Major depressive episode, ansiedad por edad y sexo |

**Por qué estos dos.** MTF mide *actitudes y conductas* reportadas; NSDUH mide *diagnósticos clínicos*. La integración es exactamente la que el libro utiliza para sostener su argumento. Cada dataset documenta su propia realidad parcial del fenómeno; juntos construyen evidencia robusta.

**Limitaciones reportadas.**
- NSDUH cambió de metodología en 2015 (rediseño del instrumento). Tratamos el cambio como punto de segmentación y lo declaramos explícitamente.
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
