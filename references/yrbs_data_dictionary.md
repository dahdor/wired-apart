# Data Dictionary — CDC YRBS (Youth Risk Behavior Surveillance System)

> _Actualizado en la revisión jun-2026, tras detectar bugs en la versión
> inicial. Las definiciones de Q4, Q5 y Q80 estaban equivocadas. **Adicional
> jun-2026:** la rama de cleaning de `attempted_suicide_yesno` para 2011-2021
> estaba invertida; ver `CHANGELOG.md` #1 y `notebooks/1.0-dh-yrbs-cleaning.ipynb`
> sección 8._

## Descripción general

El YRBS (Youth Risk Behavior Surveillance System) es un sistema de vigilancia
de conductas de riesgo en adolescentes administrado por los CDC. Realiza
encuestas bianuales a estudiantes de **9° a 12° grado** en escuelas públicas
y privadas de EE.UU. desde 1991. Mide conductas como uso de sustancias,
violencia, salud mental, actividad física, y (desde 2013) tiempo de pantalla.

**Caso especial para nuestro proyecto:** YRBS es el único survey público de
adolescentes que **combina exposición (tiempo de pantalla) con outcomes
(depresión, ideación suicida) en el mismo individuo**, lo que lo hace
particularmente útil para análisis de asociación a nivel individual.

## Descarga y formato

- **URL oficial:** https://www.cdc.gov/yrbs/data/index.html
- **Formato de distribución:** Access (`.mdb`) y ASCII
- **Ventana descargada:** **2005–2021** (años impares: 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021)
- **Driver ODBC para Python:** `Microsoft Access Driver (*.mdb, *.accdb)` (incluido en Windows)
- **Conversión a CSV/Parquet:** se hace en `notebooks/0.0-dh-data-acquisition.ipynb` y se guarda en `data/processed/yrbs_<year>.parquet` para no depender de ODBC en cada lectura.

## Variables demográficas (crudas)

| Q-code | Variable | Tipo | Valores RAW (1ª versión cleaning) | Valores CORRECTOS | Notas |
|---|---|---|---|---|---|
| `q1` | Edad | int | 1=12y, 2=13y, ..., 6=17y, 7=18+y | ✅ correcto | |
| `q2` | Sexo | int | 1=Female, 2=Male | ✅ correcto | |
| `q3` | Grado | int | 1=9°, 2=10°, 3=11°, 4=12°, 5=Ungraded/Other | ✅ correcto | |
| `q4` | **Hispanic/Latino origin** | int (binario) | "1=Yes, 2=No" | ⚠️ Solo 2007+. **2005 tiene 8 categorías** (origen hispano detallado: Mexican, Puerto Rican, etc.) | En `yrbs_clean`: `hispanic` (crudo) y `hispanic_yesno` (unificado 1=Yes, 0=No) |
| `q5` | **HEIGHT (altura)** | float | ❌ Estábamos usando como "race" | ✅ Height in meters (1.27-2.11) | NO es race. Ver `raceeth` abajo. |
| `q6` | WEIGHT (peso) | float | — | ✅ Weight in kg | |
| `raceeth` | **Raza-Etnia (derivada CDC)** | string (8 cats) | ❌ NO se usaba | ✅ 1=AI/AN, 2=Asian, 3=Black, 4=NHPI, 5=White, 6=Hispanic, 7=Multi, 8=Unknown | **Solo válida 2007+** (97%). 2005 = NaN. |
| `raceorig` | Raza original (multi-selección) | string (30 cats) | — | ⚠️ No usada | Solo 2005 (71%). |

**⚠️ Bug corregido en jun-2026:** la columna `race` en `yrbs_clean_2005_2021.parquet` ahora es `raceeth` (string, 8 cats). La versión anterior mapeaba `q5` (altura) a `race`, lo que producía valores como 1.70m en una columna categórica.

## Outcomes de salud mental (con crosswalk Q-codes)

⚠️ **Importante:** los Q-codes rotan cada 2 años para evitar priming effects
(mismo concepto, número de pregunta cambia). La redacción se mantiene
estable. **Verificamos empíricamente** que las distribuciones (% yes) por año
coinciden con el codebook oficial.

| Concepto | 2005-2009 | 2011 | 2013-2015 | 2017-2021 | Validación |
|---|---|---|---|---|---|
| sad/hopeless (depresión) | Q23 (binario) | Q24 (binario) | Q26 (binario) | Q25 (binario) | 2019=36.7% matchea CDC ✅ |
| Considered suicide | Q24 (binario) | Q25 (binario) | Q27 (binario) | Q26 (binario) | |
| Made plan | Q25 (binario) | Q26 (binario) | Q28 (binario) | Q27 (binario) | |
| **Attempted suicide (bin)** | **Q22 (binario)** | **Q27 (ordinal)** | **Q29 (ordinal)** | **Q28 (ordinal)** | 2005/07: 1=Yes/2=No; 2009-2021: 1=0 times/2=1/3=2-3/4=4-5/5=6+ |
| Attempted suicide (ord) | — | Q27 | Q29 | Q28 | Solo 2009-2021 (1–5) |
| Electronically bullied | Q21/22 | Q23 | Q25 | Q24 | |
| Bullied on school property | Q20/21 | Q22 | Q24 | Q23 | |

> ⚠️ **Codificación de attempted_suicide (jun-2026, CHANGELOG #1):** las preguntas Q27/Q28/Q29 en 2011-2021 son **ordinales** (1=0 times, 2-5 = 1+ veces), **no binarias**. El cleaning debe mapear 1→No y 2+→Yes, NO usar `map({1: 1, 2: 0})` que produciría una variable invertida. Esta es la razón por la que la rama del código de cleaning distingue explícitamente entre 2005-2007 (binario) y 2009+ (ordinal).

**Crosswalk completo y validado** en `wired_apart/dataset.py → YRBS_QCODE_CROSSWALK`.

## Exposición: Screen time (Q80)

⚠️ **CRÍTICO — solo 2019 es válido para screen time "moderno":**

| Año | Q80 en realidad | ¿Es screen time? |
|---|---|---|
| 2005–2007 | Other (mixto, no screen time) | ❌ |
| 2009 | Physical activity 60 min/day | ❌ |
| 2011 | TV watching (≥3 h/día) | ⚠️ Parcial |
| 2013 | Physical activity 60 min/day | ❌ (valor 8 = "0 days", frecuente ~25%) |
| 2015 | Physical activity 60 min/day | ❌ (valor 8 = "0 days", frecuente ~25%) |
| 2017 | **"Video/computer/games + computer not for school"** (mismo wording que 2019, según YRBS 2017 codebook oficial) | ⚠️ Válido, pero se considera "pre-smartphone-ubiquito" |
| **2019** | **"Video/computer/games + social media" (la métrica de Haidt)** | ✅ |
| 2021 | Sports teams participation | ❌ |

**Corrección jun-2026 (CHANGELOG):** la versión anterior del data dictionary afirmaba que 2017 Q80 = "TV only", pero según el codebook oficial de YRBS 2017, la redacción de Q80 es la misma que 2019 ("video or computer games or use a computer for something that is not school work"). El cambio entre 2017 y 2019 es la **adición de "social media"** en la descripción. Para mantener consistencia metodológica y evitar comparaciones problemáticas, **el análisis de screen time en este proyecto se restringe a 2019** (único año con redacción inequívocamente "moderna"). El campo `screen_time` en `yrbs_clean` contiene valores de 2017 por consistencia del crosswalk, pero el análisis los ignora.

**Conclusión:** el análisis de screen time es **transversal (2019 solamente)**, no de serie de tiempo. La `screen_time` en `yrbs_clean` tiene valores no-NaN para 2017 y 2019, pero el análisis solo usa 2019.

## Variables de diseño muestral

| Variable | Tipo | Significado |
|---|---|---|
| `weight` | float | Peso muestral. **Necesario** para análisis correcto. |
| `stratum` | float (16 valores) | Estrato del diseño muestral complejo. |
| `psu` | float (396 valores) | Primary Sampling Unit (conglomerado). |

YRBS usa un **diseño muestral complejo por conglomerados** (stratified
two-stage cluster sample). Para producir estimadores puntuales y errores
estándar correctos, todos los análisis deben usar `weight` como peso y
`stratum`+`psu` para identificar los conglomerados.

## Cambios de redacción entre años

- **2005 vs 2007+:** El formato de la pregunta de origen hispano (q4) cambió.
  En 2005 traía 8 categorías detalladas (Mexican, Puerto Rican, Central/South
  American, Cuban, Other Hispanic, Not Hispanic, Multiple Hispanic, Unknown).
  En 2007+ se simplificó a binario (Yes/No). En `yrbs_clean`:
  - `hispanic` conserva la codificación cruda (útil para 2005).
  - `hispanic_yesno` es la versión unificada (1=Yes, 0=No) para 2007+.
- **2019 vs otros años:** la pregunta de screen time (Q80) tiene redacción
  diferente (incluye social media + video games) **solo en 2019**.

## Limitaciones generales

- **Muestreo.** YRBS excluye adolescentes no escolarizados, que tienen tasas
  de depresión y suicidio más altas. Las cifras subestiman la prevalencia
  real.
- **Auto-reporte.** Las respuestas son auto-reportadas; los adolescentes
  pueden sub-reportar conductas estigmatizadas (ideación suicida) o
  sobre-reportar otras (horas de pantalla).
- **Diseño bianual.** YRBS encuesta en años impares. Para años pares no hay
  datos del survey. En gráficos temporales conectamos los puntos con líneas
  punteadas para indicar la interpolación implícita.
- **Cambios de metodología.** El cuestionario se ha revisado varias veces.
  Las variables de "screen time" solo existen desde 2013, y solo 2019
  captura la métrica de Haidt (redes sociales + video).

## Datos faltantes y valores especiales

En los archivos Access de YRBS, los valores faltantes suelen estar codificados
como números altos (e.g., 7 para Q25 cuando la respuesta es missing). En el
ASCII tienen códigos específicos. Documentamos los valores válidos y de
missing en la limpieza (Fase 3).

## Outputs limpios

- `data/processed/yrbs_2005_2021.parquet`: stacked raw, 134,674 × 230 cols.
  Contiene TODAS las q-vars + columnas derivadas CDC.
- `data/processed/yrbs_clean_2005_2021.parquet`: limpio y unificado,
  134,674 × 17 cols (15 originales + 2 nuevas en jun-2026:
  `hispanic_yesno` y `race_raw`).
