# Handoff — Wired Apart (Análisis de Datos, FPTSP27)

> Documento vivo. Léelo antes de continuar el proyecto. Contiene todo el
> contexto que se perdería en una compresión de conversación.

---

## 1. TL;DR del proyecto

- **Repo:** `https://github.com/dahdor/wired-apart` (local en `C:/Users/dahdor/workspace/projects/ad/wired-apart`)
- **Estudiante:** Diego Hernández — C.I. 31.045.867 — Unimet, FPTSP27, sección 1, Fac. Ingeniería, Dep. Gestión de Proyectos y Sistemas
- **Tema:** "Wired Apart" — cuantificar la asociación entre la transición a la "phone-based childhood" (2010-2015) y el deterioro del bienestar adolescente en EE.UU. (2005-2020)
- **Pregunta de investigación:** ¿En qué magnitud y con qué rapidez la transición a una infancia basada en el teléfono se asocia con el deterioro de indicadores de bienestar adolescente, y qué marco de monitoreo e intervención digital permite medir y revertir ese efecto en entornos escolares?
- **Plan completo** en `.agents/plans/plan-proyecto-ad.md` (9 fases)
- **Estado actual:** Fases 0-2 completas (decisiones, setup, datos). Pendiente Fase 3 (limpieza)

## 2. Lo que ya está hecho (commits)

| Commit | Qué hace |
|---|---|
| `2b6c2df` | Scaffold CCDS + uv + Quarto. Estructura de carpetas, `pyproject.toml`, `Makefile`, 8 notebooks plantilla, `_quarto.yml`, `informe.qmd` (esqueleto con 9 secciones), README con storytelling, LICENSE MIT, `.env`, `references/apa.csl`, `references/references.bib` |
| `254ce57` | **Fase 2 completa.** 9 años de YRBS (2005-2021) descargados, convertidos a Parquet, apilados en `data/processed/yrbs_2005_2021.parquet` (134,674 registros). Mortalidad adolescente 2018-2024 vía Socrata API. SHA-256 de todos los archivos en `references/data_provenance.md` |
| `6e5fd41` | Fix de portabilidad: agregada sección "Sin make" al README con equivalentes `uv run` |

## 3. Pivote crítico: MTF/NSDUH → YRBS + NCHS

**Decisión que se mantuvo tras debate con Diego:** cambiar los datasets originales.

| Original (Ruta A) | Real |
|---|---|
| MTF (ICPSR) + NSDUH (SAMHSA) | YRBS (CDC público) + NCHS Socrata (público) |
| Ambos requieren registro que no se puede automatizar | 100% descargables, sin registro |
| ICPSR no se puede scrapear (Cloudflare) | URLs directas en `www.cdc.gov/yrbs/files/...` |

**Por qué YRBS es estrictamente superior para nuestro análisis:**
1. Tiene **ambas variables en el mismo dataset**: exposición (Q80 = horas de pantalla incluyendo social media) y outcomes (Q25-Q28 = tristeza, ideación suicida, intentos)
2. Cobertura 2005-2021, 9 años, ~15k estudiantes/año
3. Es **el mismo dataset que el libro usa para la Figura 1.4** (visitas a urgencias por autolesión), así que estamos en terreno conocido
4. Pesos muestrales (`weight`, `stratum`, `psu`) para análisis con diseño complejo

**NCHS Socrata** provee mortalidad por suicidio adolescente (2018-2024). 2005-2017 pendientes (ver §6).

## 4. Convención de nombres y estructura

**Notebooks:** `N.N-{iniciales}-{descripcion}.ipynb` con iniciales `dh` (Diego Hernández). CCDS convention. NO cambiar.

**Módulo Python:** `wired_apart/` con:
- `config.py` — rutas, paleta, ventana 2005-2020, constantes
- `dataset.py` — `load_yrbs()`, `load_wonder()`, `sha256_of()`
- `features.py` — cohortes, períodos Great Rewiring, `rate_per_100k()`, `zscore()`
- `plots.py` — `apply_project_style()`, `save()`, `highlight_period()` (sombras 2010-2015)

**Datos:**
- `data/raw/yrbs/yrbs{year}.mdb` + codebook PDF (no se commitean a git, ignorados)
- `data/raw/cdc/` (reservado para WONDER, vacío por ahora)
- `data/interim/yrbs/yrbs{year}.parquet` (por año, sí se commitean)
- `data/processed/yrbs_2005_2021.parquet` (stacked, sí se commitea)
- `data/processed/wonder_suicide_adolescent_2018_2024.csv` (sí se commitea)

**Referencias:**
- `references/data_provenance.md` — generado por el notebook 0.0
- `references/yrbs_data_dictionary.md` — escrito a mano, mapeo de Q-codes
- `references/wonder_data_dictionary.md` — escrito a mano
- `references/references.bib` — BibTeX con Haidt 2024, Twenge 2017, Dawson 2020, CDC, SAMHSA, MTF

## 5. Estilo de evaluación de Carolina (lo que ella mira)

Crucé `p1/correcciones.md` y `prac1/correcciones.md`. Patrones que importan:

- **Orden metodológico estricto:** tipos → categorías → valores imposibles → *después* imputar. (Carolina lo señaló literal en p1: "imputar antes de revisar inconsistencias era un riesgo que se mencionaba en la justificación".)
- **Cero "obviedades":** cada conversión, winsorización, descarte de duplicado tiene justificación + verificación post-acción.
- **SMART con metas cuantitativas:** no "analizar el uso" sino "aumentar 10-15%". En la propuesta de solución, decir exactamente qué intervención se prueba (A/B) y qué cambio se mide.
- **Storytelling > análisis técnico:** 7 plantillas de Dawson C9 obligatorias (cambio en el tiempo, intersecciones, contraste, drill-down, outliers, zoom-out, factores).
- **Estructura diagnóstico → decisión → verificación** en cada bloque (literal del enunciado del p1).
- **Frases recurrentes:** "buen trabajo / buen pensamiento" + "pero hay que cuidar los detalles / el principal punto de mejora es...". Aprueba el approach pero exige rigor en detalles.

**Implicación para la limpieza (Fase 3):** cada paso en cada notebook de limpieza debe tener celda markdown explícita de **diagnóstico → decisión → verificación**. No "eliminamos outliers" sino "diagnosticamos X outliers por encima de p99 → decidimos winsorizar al p99 porque [razón] → verificamos que la distribución ahora tiene kurtosis < 5".

## 6. Pendientes / problemas abiertos

### 6.1. WONDER 2005-2017 (mortalidad adolescente)

Socrata solo tiene 2018-2024. Para tener la serie completa 2005-2020 necesitamos 2005-2017. Opciones:

1. **WONDER API directa (D77/D76):** funciona pero requiere XML muy específico + rate limit de 15s/request. Probé varias versiones y me dio errores de validación constantes. La doc está en https://wonder.cdc.gov/wonder/help/wonder-api.html
2. **WONDER UI manual:** abrir el form, enviar query, exportar TSV. Más simple pero no es "reproducible" en el sentido estricto.
3. **NCHS Data Briefs (PDFs oficiales):** hay tablas con series anuales. Habría que scrapear o extraer las tablas. Candidatos: NCHS Data Brief No. 471 (2023) tiene 2001-2021.
4. **NVSS annual mortality tables:** los "Deaths: Final Data" anuales tienen series largas.

**Recomendación post-compresión:** probar de nuevo la WONDER API con el ejemplo2 funcionando (que es la consulta por "Injury Intent" para menores de 18), después de esperar 15s entre intentos. Si no funciona en 1-2 intentos, ir a opción 3 (Data Briefs).

### 6.2. NCHS Socrata devuelve 10-year age groups (15-24, no 15-19)

Para nuestro análisis queremos 10-14 y 15-19 específicamente. El dataset `w26f-tf3h` los tiene pero como "Sex and age group" subgroup los devuelve en grupos de 10 años. Tenemos los datos de "Female: 10-14 years" y "Male: 10-14 years" — sí existen en la API, pero la categoría "15-19" no aparece. **Confirmar si el subgrupo "15-19 years" existe**, si no, decidir si usamos "15-24" como proxy o usamos otra fuente.

### 6.3. Notebook construction

Hay un patrón frágil: editar `.ipynb` con `edit` o `bash sed` puede romper el JSON (encoding cp1252 vs utf-8 en Windows, comillas escapadas, etc.). **Patrón seguro:** construir el notebook con un script Python que escribe el JSON limpio. Ver §7.

## 7. Quirks de herramientas y entorno

### Windows / paths
- `quarto` **no está en PATH** en este Windows. Usar path completo: `C:/Users/dahdor/AppData/Local/Programs/Quarto/bin/quarto.exe` o `uv run quarto ...` que sí funciona porque `uv` resuelve desde el venv.
- `make` solo está disponible porque Gow está instalado. El README ya tiene sección "sin make" con `uv run` equivalents.
- `mdb-export` (mdbtools) **no está** en Windows. La estrategia que funcionó es `pyodbc` con el driver ODBC de Microsoft Access (incluido en Windows).
- `uv` está en `C:/Users/dahdor/AppData/Local/Microsoft/WinGet/...` y funciona desde cualquier path.

### Python notebooks
- Para ejecutar un notebook end-to-end: `uv run --with jupyter --with <otras-deps> jupyter execute notebooks/N.N-dh-xxx.ipynb`
- El encoding del notebook file es cp1252 cuando lo escribe `jupyter execute` en este Windows. Si lo editas con `edit` o con `bash python json.dump`, usar `encoding='cp1252'` o ser cuidadoso con caracteres no-ASCII.
- Las comillas dentro de strings en celdas con `chr(96)` para backticks es el patrón seguro para evitar shell escaping.

### YRBS lectura
- **Driver ODBC funciona en Windows.** La string de conexión es `r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ={path};"`
- La tabla principal es `XXHq` (en algunos años `XXH2017_YRBS_Data` o similar). El notebook de acquisition itera sobre `tables` para encontrar la no-MSys.
- **Las q-vars vienen como strings**, no enteros. Hay que convertirlas con `pd.to_numeric(..., errors='coerce')` antes de cualquier operación numérica.
- `weight`, `stratum`, `psu` también vienen como strings/floats mezclados.

### WONDER/Socrata
- `group` es palabra reservada en SoQL → usar backticks: `` `group`='Sex and age group' ``
- `like '%crude%'` requiere encoding correcto de `%` en URL → preferible filtrar crude en pandas después de traer todo
- WONDER API rate limit: 15s entre requests mínimo

## 8. Plan de las próximas fases (orden estricto)

### Fase 3 — Limpieza (PRIORIDAD, Carolina mira acá con lupa)

Notebooks a llenar: `1.0-dh-yrbs-cleaning.ipynb` y `1.1-dh-nsduh-cleaning.ipynb` (renombrar a `1.1-dh-wonder-cleaning.ipynb` para reflejar el pivot).

**Estructura por notebook (orden metodológico que Carolina exige):**
1. Diagnóstico inicial — shape, dtypes, head, NaN counts
2. Normalización de tipos — q-vars a int/float, fechas, etc.
3. Consistencia de categorías — mayúsculas, acentos, typos
4. Valores imposibles — Q1 age > 7, Q2 sex not 1-2, Q25 not 1-2, Q80 not 1-7, etc.
5. Duplicados — análisis de claves, justificación del descarte
6. Outliers — IQR + winsorización para Q80 (horas de pantalla)
7. Faltantes — patrón MCAR/MAR/MNAR, decisión imputar/eliminar
8. Verificación final — shape, distribuciones, sanity checks

**Cada paso con celda markdown de diagnóstico → decisión → verificación.**

Output: `data/processed/yrbs_clean_2005_2021.parquet` y `data/processed/wonder_clean_2018_2024.csv`.

### Fase 4 — EDA (notebooks 2.0 y 2.1)

Visualizaciones exploratorias narradas. Generar al menos 5-8 figuras con interpretación.

### Fase 5 — Análisis principal (notebook 3.0)

Integración MTF/WONDER (ahora YRBS/NCHS), correlaciones por segmento, paradoja de Simpson, pruebas de hipótesis, análisis de sensibilidad.

### Fase 6 — Storytelling (notebook 4.0)

Aplicar las 7 plantillas de Dawson C9. Guardar figuras en `reports/figures/`.

### Fase 7 — Solución de ingeniería (notebook 5.0)

Framework "Phone-Free Schools" con métricas de proceso y resultado.

### Fase 8 — README final (rellenar los placeholders)

### Fase 9 — Informe Quarto (rellenar `informe.qmd`)

Front matter con logo unimet, cédula, código materia. Bibliografía del libro.

### Fase 10 — Polish contra correcciones de Carolina

## 9. Cosas que Diego ya validó

- Ruta A (análisis del libro) — ✅
- Repo `wired-apart` — ✅
- MTF + NSDUH como datasets — pivoteó a YRBS + NCHS — ✅
- Ventana 2005-2020 — ✅
- "dh" en notebook names — ✅ (después de un malentendido mío)
- Notebooks con make y uv — ✅

## 10. Cosas que Diego debe decidir cuando vuelva

1. **WONDER 2005-2017:** seguir con WONDER API, WONDER UI manual, NCHS Data Briefs (PDF scraping), o aceptar la limitación y declarar 2018-2024 en el informe.
2. **Rango de edad para NCHS Socrata:** usar "15-24" como proxy de "15-19" (suboptimal) o buscar otra fuente que tenga 15-19 específicamente.
3. **Nombre del proyecto en GitHub:** ya creado el repo, falta confirmar el push y la descripción pública.

## 11. Cómo retomar el trabajo

```bash
cd C:/Users/dahdor/workspace/projects/ad/wired-apart
git status                    # debería estar limpio
git log --oneline            # ver los 3 commits
ls data/processed/            # verificar yrbs_2005_2021.parquet existe
uv run --with jupyter --with pyodbc --with pandas --with pyarrow \
  jupyter execute notebooks/0.0-dh-data-acquisition.ipynb
```

Si todo carga, empezar Fase 3 con el notebook de limpieza de YRBS.

## 12. Referencias rápidas en el repo

- Plan completo: `.agents/plans/plan-proyecto-ad.md`
- Enunciado del proyecto: `enunciado-proyecto.md` (en la raíz del workspace ad/)
- Correcciones de Carolina: `p1/correcciones.md` y `prac1/correcciones.md` (raíz del workspace)
- Dawson C9 (storytelling): `content/dawson/Dawson C9 - Data Storytelling and Visualization copy.md`
- Clase 7 (visualización y storytelling): `content/lessons/Clase 7 - Visualización y Storytelling.md`
- The Anxious Generation: `content/the-anxious-generation/` (12 capítulos + conclusión + intro)

## 13. Mi próximo paso concreto cuando retomemos

**Empezar `1.0-dh-yrbs-cleaning.ipynb`** con la estructura completa de 8 pasos. Antes de eso, decidir el approach para WONDER 2005-2017 (intentar WONDER API una vez más con rate limit respetado, si falla, declarar 2018-2024 en el informe y justificar).

---

**TL;DR de este handoff:**
- Proyecto: análisis cuantitativo del impacto de la "phone-based childhood" sobre bienestar adolescente US
- Repo local: `wired-apart/`, 3 commits, 134k registros YRBS cargados
- Pivote: MTF/NSDUH → YRBS + NCHS (documentado en README)
- Siguiente: Fase 3 (limpieza), donde más mira Carolina
- Quirks: `quarto` no en PATH, `make` opcional, YRBS requiere ODBC de Windows, WONDER API problemática
- Pendiente: WONDER 2005-2017 (mortalidad adolescente)
