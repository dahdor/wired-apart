# Handoff — Wired Apart (Análisis de Datos, FPTSP27)

> Documento vivo. Léelo antes de continuar el proyecto. Contiene todo el
> contexto que se perdería en una compresión de conversación.

---

## 1. TL;DR del proyecto

- **Repo:** `https://github.com/dahdor/wired-apart` (local en `C:/Users/dahdor/workspace/projects/ad/wired-apart`)
- **Estudiante:** Diego Hernández — C.I. 31.045.867 — Unimet, FPTSP27, sección 1, Fac. Ingeniería, Dep. Gestión de Proyectos y Sistemas
- **Tema:** "Wired Apart" — cuantificar la asociación entre la transición a la "phone-based childhood" (2010-2015) y el deterioro del bienestar adolescente en EE.UU. (2005-2021)
- **Pregunta de investigación:** ¿En qué magnitud y con qué rapidez la transición a una infancia basada en el teléfono se asocia con el deterioro de indicadores de bienestar adolescente, y qué marco de monitoreo e intervención digital permite medir y revertir ese efecto en entornos escolares?
- **Plan completo** en `.agents/plans/plan-proyecto-ad.md` (10 fases)
- **Estado actual (junio 2026):** Fases 0-3 completas, Fase 4 parcial. **Limpieza hecha para YRBS y WONDER. 5 figuras narradas listas.**

## 2. Commits del proyecto (8)

| Hash | Mensaje | Qué hace |
|---|---|---|
| `2b6c2df` | chore: scaffold wired-apart project | CCDS + uv + Quarto. Estructura, pyproject, Makefile, 8 notebooks plantilla, _quarto.yml, informe.qmd, README, LICENSE |
| `254ce57` | feat(data): acquire YRBS + NCHS | 9 años YRBS (2005-2021) en `data/raw/yrbs/`. Convertidos a Parquet. Socrata 2018-2024. |
| `6e5fd41` | docs(readme): portable no make | Sección "Sin make" con uv run equivalents |
| `b333379` | docs(handoff): handoff doc | (este archivo) |
| `5c72097` | feat(cleaning): YRBS 1.0 | Notebook 1.0 con crosswalk Q-codes. Output: `yrbs_clean_2005_2021.parquet` |
| `7a203a0` | feat(cleaning): WONDER 1.1 | Notebook 1.1 con augmentación HUS 2018. Output: `wonder_clean_2005_2024.csv` |
| `f1d8ebe` | chore(gitignore): track cleaned outputs | Acepta data/processed y data/external en git |
| `3cbdd52` | feat(eda): YRBS EDA 2.0 | 5 figuras narradas en reports/figures/ |

## 3. Datasets finales (después de limpieza)

### YRBS (`data/processed/yrbs_clean_2005_2021.parquet`)
- **134,674 registros × 15 columnas**
- 9 años (2005-2021, bianual en impares)
- Variables: `year`, `age`, `sex`, `grade`, `hispanic`, `race`, `weight`, `stratum`, `psu`, `sad_hopeless`, `considered_suicide`, `made_plan`, `attempted_suicide_yesno`, `attempted_suicide_ordinal`, `screen_time`
- Validado: 2019 sad/hopeless = 36.7% (matches CDC oficial)

### WONDER/NCHS (`data/processed/wonder_clean_2005_2024.csv`)
- **40 filas × 9 columnas** (12 HUS 2018 + 28 Socrata)
- 10 años con datos: 2010, 2016, 2017, 2018-2024
- 4 grupos demográficos: Female/Male × 10-14/15-19
- Gaps: 2005-2009, 2011-2015 (WONDER API caída)

## 4. Pivote crítico: MTF/NSDUH → YRBS + NCHS

**Decisión que se mantuvo tras debate con Diego:** cambiar los datasets originales.

| Original (Ruta A) | Real |
|---|---|
| MTF (ICPSR) + NSDUH (SAMHSA) | YRBS (CDC público) + NCHS Socrata (público) |
| Ambos requieren registro que no se puede automatizar | 100% descargables, sin registro |
| ICPSR no se puede scrapear (Cloudflare) | URLs directas en `www.cdc.gov/yrbs/files/...` |

**Por qué YRBS es estrictamente superior para nuestro análisis:**
1. Tiene **ambas variables en el mismo dataset**: exposición (Q80 = horas de pantalla incluyendo social media) y outcomes (Q25-Q28 = tristeza, ideación suicida, intentos)
2. Cobertura 2005-2021, 9 años, ~15k estudiantes/año
3. Es **el mismo dataset que el libro usa para la Figura 1.4** (visitas a urgencias por autolesión)

**NCHS Socrata** provee mortalidad por suicidio adolescente (2018-2024). 2005-2017 resuelto con HUS 2018 Table 9 (PDF público, solo 3 puntos: 2010, 2016, 2017).

## 5. Hallazgos críticos durante la limpieza

### 5.1. Q-codes rotan cada 2 años en YRBS

**Descubrimiento.** Los Q-codes (Q25, Q80, etc.) rotan cada 2 años en YRBS para evitar priming effects. La **redacción** se mantiene estable, pero el número de pregunta cambia.

**Crosswalk validado** (`wired_apart/dataset.py` → `YRBS_QCODE_CROSSWALK`):

| Concepto | 2005-2009 | 2011 | 2013-2015 | 2017-2021 |
|---|---|---|---|---|
| sad/hopeless | Q23 | Q24 | Q26 | Q25 |
| considered_suicide | Q24 | Q25 | Q27 | Q26 |
| made_plan | Q25 | Q26 | Q28 | Q27 |
| attempted_suicide | Q22/Q26* | Q27 | Q29* | Q28 |

*2009 y 2013-2015 tienen codificación ordinal (0/1/2-3/4-5/6+), no binaria.

**Validación empírica:** la columna con 25-40% YES (depresión) coincide exactamente con el codebook para cada año.

### 5.2. Q80 ≠ screen time en casi todos los años

- 2009, 2013, 2015: Q80 = "physical activity 60 min/day"
- 2011, 2017: Q80 = "watch TV"
- **2019: Q80 = "video/computer/games/social media" (la métrica de Haidt)**
- 2021: Q80 = "sports teams"

**Conclusión:** solo 2019 tiene la exposición correcta. El análisis de screen time es transversal, no de serie de tiempo.

### 5.3. WONDER API completamente caída

- D76, D77, D158, D176: **TODAS devuelven HTTP 400 "intermittent error"** para CUALQUIER query (incluso minimal all-cause 2020).
- Probado con 15s, 20s, 30s de rate limit. Sin éxito.
- **Decisión:** aceptar limitación, workaround con HUS 2018 + Socrata.

## 6. Convención de nombres y estructura

**Notebooks:** `N.N-{iniciales}-{descripcion}.ipynb` con iniciales `dh`. CCDS convention. NO cambiar.

**Módulo Python:** `wired_apart/`:
- `config.py` — rutas, paleta, ventana 2005-2020, constantes
- `dataset.py` — `load_yrbs_processed()`, `load_wonder_processed()`, `YRBS_QCODE_CROSSWALK`, `sha256_of()`
- `features.py` — cohortes, períodos Great Rewiring, `rate_per_100k()`, `zscore()`
- `plots.py` — `apply_project_style()`, `save()`, `highlight_period()` (con kwargs `color` y `alpha`)

**Datos:**
- `data/raw/yrbs/yrbs{year}.mdb` + codebook PDF (ignorado por git, 280 MB total)
- `data/raw/cdc/` (vacío, ignorado)
- `data/interim/yrbs/yrbs{year}.parquet` (por año, tracked, ~10 MB total)
- `data/processed/yrbs_2005_2021.parquet` (stacked raw, tracked, 6.5 MB)
- `data/processed/yrbs_clean_2005_2021.parquet` (limpio, tracked, 590 KB)
- `data/processed/wonder_suicide_adolescent_2018_2024.csv` (Socrata, tracked)
- `data/processed/wonder_clean_2005_2024.csv` (limpio + HUS, tracked, 40 filas)
- `data/external/db471.pdf` (NCHS Data Brief 471, tracked, 405 KB)
- `data/external/hus2018_table9.pdf` (HUS Table 9, tracked, 196 KB)

**Figuras (reports/figures/):**
- `fig1_sad_hopeless_trend.png` (240 KB)
- `fig2_sex_gap.png` (209 KB) — la más impactante
- `fig3_drill_down.png` (144 KB)
- `fig4_multi_panel.png` (295 KB)
- `fig5_screen_sad_2019.png` (161 KB)

**Referencias:**
- `references/data_provenance.md` — generado por notebook 0.0 + actualizado en 1.1
- `references/yrbs_data_dictionary.md` — escrito a mano
- `references/wonder_data_dictionary.md` — escrito a mano
- `references/references.bib` — BibTeX con Haidt 2024, Twenge 2017, Dawson 2020, CDC, SAMHSA, MTF

## 7. Estilo de evaluación de Carolina (lo que ella mira)

Crucé `p1/correcciones.md` y `prac1/correcciones.md`. Patrones que importan:

- **Orden metodológico estricto:** tipos → categorías → valores imposibles → *después* imputar.
- **Cero "obviedades":** cada conversión, winsorización, descarte de duplicado tiene justificación + verificación post-acción.
- **SMART con metas cuantitativas:** no "analizar el uso" sino "aumentar 10-15%".
- **Storytelling > análisis técnico:** 7 plantillas de Dawson C9 obligatorias.
- **Estructura diagnóstico → decisión → verificación** en cada bloque.
- **Frases recurrentes:** "buen trabajo / buen pensamiento" + "pero hay que cuidar los detalles".

**Implicación cumplida:** los notebooks 1.0 y 1.1 tienen celdas markdown explícitas de **diagnóstico → decisión → verificación** en cada paso. EDA 2.0 usa 5 de las 7 plantillas de Dawson.

## 8. Hallazgos cuantitativos del EDA (para el informe)

### 8.1. Tendencia global
- sad/hopeless overall: 28.6% (2005) → **41.0% (2021)** = +43% en 16 años
- considered suicide: 17% (2005) → 21% (2021) = +25%
- made plan: 13% (2005) → 17% (2021) = +29%

### 8.2. Asimetría de género (LA CIFRA CLAVE)
| | 2005 | 2021 | Δ |
|---|---|---|---|
| Mujeres sad/hopeless | 36.4% | **55.6%** | +19.2pp (+53%) |
| Hombres sad/hopeless | 20.1% | 28.0% | +7.9pp (+39%) |
| **Gap F-M** | **16.3pp** | **27.6pp** | **+11.3pp (+70%)** |

**Para 2021, más de la mitad de las mujeres adolescentes reportan sad/hopeless 2+ semanas.**

### 8.3. Punto de inflexión
- 2015-2017: +1.6pp (5%)
- 2017-2019: +5.1pp (16%) — primer salto sostenido
- 2019-2021: +4.8pp (13%) — aceleración COVID叠加

### 8.4. Screen time 2019
- 5+ horas/día: ~50% sad/hopeless
- No usa: ~30% sad/hopeless
- Asociación monotónica clara (~1.5x)

## 9. Pendientes / problemas abiertos

### 9.1. Mortalidad adolescente 2005-2009 y 2011-2015
**Status: gap documentado, no resoluble en este entorno.**
- WONDER API caída en todos los endpoints
- HUS Table 9 no tiene años intermedios (solo 2010, 2016, 2017)
- Alternativa futura: scraping de NVSS annual mortality tables o WONDER UI manual

### 9.2. Screen time como serie de tiempo
**Status: limitación aceptada, análisis transversal 2019.**
- Solo 2019 tiene Q80 con la redacción correcta
- 2017: TV only. 2021: sports teams.
- **Decisión:** análisis cross-sectional 2019, no serie de tiempo.

### 9.3. Notebook construction (encoding)
- **Patrón seguro:** construir con script Python usando `ensure_ascii=True` (escapa tildes a `\u00e1` etc.)
- `jupyter execute` en Windows lee con cp1252 por default → falla con UTF-8 directo
- `PYTHONIOENCODING=utf-8` no soluciona el problema de read
- **Workflow:** escribir con `ensure_ascii=True`, luego `nbformat.read` y `nbformat.write` para normalizar IDs
- **CRÍTICO:** `jupyter execute` NO guarda los outputs en el archivo .ipynb. Usar en su lugar:
  `jupyter nbconvert --to notebook --execute --inplace`

### 9.4. BUG en cleaning: columna 'race' es ALTURA
**Status: bug detectado en análisis 3.0, no corregido todavía.**
- La columna 'race' en `yrbs_clean_2005_2021.parquet` realmente contiene **altura en metros** (valores 1.50-2.10)
- Origen: error en el mapping del notebook 1.0 (cleaning). Un q-code (probablemente q4 o q5) terminó mapeado a 'race' cuando era height
- 121,555 valores NaN (90%) y 13,119 con valores de altura reales
- **Workaround aplicado:** análisis 3.0 Simpson usa 'hispanic' (8 categorías válidas) en lugar de 'race'
- **Pendiente:** re-examinar cleaning 1.0, identificar q-code real de race, re-mapping. Probablemente afecta el notebook 1.0 (lo cambió de 'q4' o 'q5' a 'race' por error)

## 10. Quirks de herramientas y entorno

### Windows / paths
- `quarto` **no está en PATH**. Usar `uv run quarto ...` (resuelve desde venv).
- `make` solo disponible porque Gow está instalado. README tiene sección "sin make".
- `mdb-export` (mdbtools) **no está**. Usar `pyodbc` con driver ODBC Windows.
- `uv` funciona desde cualquier path.

### Python notebooks
- `uv run --with <deps> jupyter execute <notebook>` para ejecutar end-to-end
- Encoding: usar `ensure_ascii=True` al escribir con `json.dump` o construir el notebook con script Python
- `nbformat.read` + `nbformat.write` normaliza los IDs de celdas

### YRBS lectura
- Driver ODBC Windows funciona
- String: `r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ={path};"`
- Tabla principal: `XXHq` (o similar por año)
- **q-vars vienen como strings** → `pd.to_numeric(..., errors='coerce')`
- `weight`/`stratum`/`psu` también strings/floats mezclados

### WONDER/Socrata
- `group` es reservada en SoQL → backticks: `` `group`='Sex and age group' ``
- LIKE con `%` requiere URL encoding correcto → preferible filtrar en pandas
- WONDER API: 400 para TODO (problema del lado de CDC, no del nuestro)

## 11. Plan de las próximas fases

### Fase 4 (continuar)
- [x] 2.0-dh-eda-yrbs.ipynb (5 figuras)
- [ ] 2.1-dh-eda-wonder.ipynb (mortalidad, 2-3 figuras con interpolación explícita del gap)

### Fase 5 — Análisis principal
- [ ] 3.0-dh-analysis.ipynb:
  - Correlaciones Pearson/Spearman entre outcomes
  - Paradoja de Simpson: análisis por subgrupos (sexo × grado × raza)
  - Regresión logística: P(sad_hopeless) ~ year + sex + age + screen_time
  - Análisis de sensibilidad con/sin pesos muestrales
  - Test de tendencias (Cochran-Armitage)
  - Comparación con mortalidad (2018-2024)

### Fase 6 — Storytelling
- [ ] 4.0-dh-storytelling.ipynb:
  - 2-3 figuras adicionales con las 7 plantillas Dawson C9
  - Outliers: ¿qué adolescentes están MEJOR que la tendencia? (zoom-in)
  - Zoom-out: comparación con NCHS mortality

### Fase 7 — Solución de ingeniería
- [ ] 5.0-dh-solution.ipynb:
  - Framework "Phone-Free Schools" con métricas SMART
  - Definición operacional de variables
  - Diseño de A/B test con power analysis
  - Costos estimados

### Fase 8 — README final
- [ ] Reemplazar placeholders con datos reales del análisis
- [ ] Badges, screenshots, etc.

### Fase 9 — Informe Quarto
- [ ] Rellenar `informe.qmd` con las 9 secciones
- [ ] Incrustar las 5+ figuras
- [ ] Bibliografía

### Fase 10 — Polish contra correcciones de Carolina
- [ ] Releer p1 y prac1 correcciones
- [ ] Verificar orden metodológico, justificación de cada transformación
- [ ] Verificar objetivos SMART con métricas

## 12. Cómo retomar el trabajo

```bash
cd C:/Users/dahdor/workspace/projects/ad/wired-apart
git status                    # working tree clean
git log --oneline            # ver los 8 commits
ls data/processed/            # verificar yrbs_clean + wonder_clean
ls reports/figures/           # verificar 5 figuras

# Re-ejecutar pipeline (opcional, ya está commiteado)
uv sync --all-extras
PYTHONIOENCODING=utf-8 uv run --with jupyter --with pandas --with pyarrow \
  jupyter execute notebooks/2.0-dh-eda-yrbs.ipynb

# Empezar Fase 4 continuación: 2.1 EDA WONDER
```

## 13. Referencias rápidas en el repo

- Plan completo: `.agents/plans/plan-proyecto-ad.md`
- Enunciado del proyecto: `enunciado-proyecto.md` (raíz del workspace `ad/`)
- Correcciones de Carolina: `p1/correcciones.md` y `prac1/correcciones.md` (raíz)
- Dawson C9 (storytelling): `content/dawson/Dawson C9 - Data Storytelling and Visualization copy.md`
- Clase 7 (visualización y storytelling): `content/lessons/Clase 7 - Visualización y Storytelling.md`
- The Anxious Generation: `content/the-anxious-generation/` (12 capítulos + conclusión + intro)

## 14. TL;DR ejecutivo

**Lo que tenemos:**
- 8 commits limpios
- 134,674 registros YRBS limpios (9 años)
- 40 filas de mortalidad adolescente limpia (10 años con gaps)
- 5 figuras narradas de alta calidad (incluyendo la del gap de género amplificándose)
- Crosswalk validado de Q-codes
- Limitaciones documentadas honestamente

**Lo que falta:**
- EDA WONDER (Fase 4 continuación)
- Análisis principal con regresiones (Fase 5)
- Storytelling adicional (Fase 6)
- Solución Phone-Free Schools (Fase 7)
- Rellenar informe.qmd (Fase 9)

**Historia del proyecto:** El aumento de sad/hopeless en mujeres adolescentes de 36% (2005) a 56% (2021) coincide con la "phone-based childhood" teorizada por Haidt. El gap de género se amplió de 16pp a 27.6pp, consistente con la hipótesis del libro de que las plataformas image-based (Instagram, TikTok) afectan desproporcionadamente a las mujeres.

**Decisiones pendientes con Diego:**
- ¿Cómo presentar el gap 2005-2017 de mortalidad en el informe? (gráfico con interpolación punteada, o tabla con "data not available" explícito)
- ¿Vale la pena un análisis más profundo del COVID叠加 (2019-2021) o quedarnos con la narrativa pre/post?
- ¿El framework Phone-Free Schools debe ser específico (recoger celulares en la puerta) o sistémico (política estatal)?

**Siguiente paso concreto:** Construir 2.1-dh-eda-wonder.ipynb con la tendencia de mortalidad 2010-2024 (con gaps explícitos como línea punteada). Después 3.0 con la regresión principal.
