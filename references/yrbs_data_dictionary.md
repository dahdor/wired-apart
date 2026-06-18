# Data Dictionary — CDC YRBS (Youth Risk Behavior Surveillance System)

> _Actualizado en la Fase 2 del proyecto, después de descargar los datos._

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
- **Ventana descargada:** 2005–2019 (años impares: 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019)
- **Driver ODBC para Python:** `Microsoft Access Driver (*.mdb, *.accdb)` (incluido en Windows)
- **Conversión a CSV/Parquet:** se hace en `notebooks/0.0-dh-data-acquisition.ipynb` y se guarda en `data/processed/yrbs_<year>.parquet` para no depender de ODBC en cada lectura.

## Variables de interés para este proyecto

| Variable YRBS | Variable cruda (Q-code) | Tipo | Valores | Uso en el análisis |
|---|---|---|---|---|
| Año de encuesta | (metadato del archivo) | int | 2005-2019 | Línea temporal principal |
| Edad | `q1` | int | 1=12y, 2=13y, ..., 7=18+y | Segmentación |
| Sexo | `q2` | int | 1=Female, 2=Male | **Segmentación por género** (clave para Haidt cap. 6) |
| Grado | `q3` | int | 1=9°, 2=10°, 3=11°, 4=12° | Segmentación |
| Hispanidad | `q4` | int | 1=Yes, 2=No | Covariable |
| Raza (multi) | `q5` (multi-selección) | int por cat | 1=AI/AN, 2=Asian, 3=Black, 4=NH/PI, 5=White, 6=Hispanic/Latino (overlap) | Covariable |
| **Sad or hopeless (depresión)** | **`q25`** | int | 1=Yes, 2=No | **Outcome principal: depresión autopercibida** |
| Considered suicide | `q26` | int | 1=Yes, 2=No | Outcome secundario |
| Made a suicide plan | `q27` | int | 1=Yes, 2=No | Outcome secundario |
| Attempted suicide | `q28` | int | 1-5 (veces) | Outcome secundario |
| **TV watching (horas/día)** | **`q79`** | int | 1=No, 2=<1h, 3=1h, 4=2h, 5=3h, 6=4h, 7=5+h | Exposición parcial |
| **Screen time (horas/día, incluye social media)** | **`q80`** | int | 1=No, 2=<1h, 3=1h, 4=2h, 5=3h, 6=4h, 7=5+h | **Exposición principal** |
| Peso muestral | `weight` | float | — | **Necesario** para análisis correcto |
| Estrato | `stratum` | float | — | Necesario para diseño muestral complejo |
| PSU | `psu` | float | — | Necesario para diseño muestral complejo |

## Pesos muestrales y diseño complejo

YRBS usa un **diseño muestral complejo por conglomerados** (stratified
two-stage cluster sample). Para producir estimadores puntuales y errores
estándar correctos, todos los análisis deben usar `weight` como peso y
`stratum`+`psu` para identificar los conglomerados. En Python usamos
`statsmodels` con su soporte para diseño muestral complejo.

**Implicación para el informe:** reportamos estimaciones ponderadas
(porcentajes de la población) y usamos los pesos para todos los análisis
inferenciales.

## Cambios de redacción entre años

Las preguntas se renumeran en algunos años. Por ejemplo, la pregunta de
"tiempo de pantalla" (Q80 en 2019) no existía antes de 2013. La pregunta
"tristeza/sin esperanza" (Q25) ha estado presente consistentemente desde
2005 pero su ubicación en el cuestionario ha cambiado. Documentamos cada
cambio en la limpieza (Fase 3) con tabla de mapeo entre años.

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
  Las variables de "screen time" solo existen desde 2013. Documentamos
  explícitamente qué variables están disponibles en qué años.

## Datos faltantes y valores especiales

En los archivos Access de YRBS, los valores faltantes suelen estar codificados
como números altos (e.g., 7 para Q25 cuando la respuesta es missing). En el
ASCII tienen códigos específicos. Documentamos los valores válidos y de
missing en la limpieza (Fase 3).
