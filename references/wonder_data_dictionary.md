# Data Dictionary — CDC WONDER (Underlying Cause of Death)

> _Actualizado en la Fase 2 del proyecto, después de la consulta a la API._

## Descripción general

CDC WONDER (Wide-ranging Online Data for Epidemiologic Research) provee
acceso a множество de datasets de salud pública. Para este proyecto usamos
**Underlying Cause of Death, 1999-2020** (basado en ICD-10), que contiene
muertes por suicidio (ICD-10 X60-X84, X87.0) y la población subyacente, con
granularidad por edad, sexo, año y raza.

**Caso especial para nuestro proyecto:** WONDER provee los outcomes de
**mortalidad** (suicidios consumados) que YRBS no captura porque su muestra
son solo estudiantes de high school. Permite análisis de tendencia agregada
poblacional y desagregación por edad (10-14, 15-19) y sexo.

## Acceso y formato

- **URL oficial:** https://wonder.cdc.gov/ucd-icd10.html
- **API:** https://wonder.cdc.gov/controller/datarequest/D176 (específica para este dataset)
- **Formato de descarga:** texto tabulado (TSV) que se convierte a CSV
- **Ventana descargada:** 2005–2020 (alineada con YRBS, dejando margen pre y post Great Rewiring)
- **Granularidad:** deaths + population + crude_rate + age_adjusted_rate por año, edad, sexo

## Variables de la extracción

| Variable | Tipo | Significado |
|---|---|---|
| `Year` | int | Año de la muerte (2005-2020) |
| `Single-Year Ages` o `Ten-Year Age Groups` | str | Edad al morir (10-14, 15-19) |
| `Gender` | str | Male, Female |
| `Deaths` | int | Conteo de muertes por suicidio (ICD-10 X60-X84) |
| `Population` | int | Población estimada (censo) |
| `Crude Rate` | float | Tasa cruda por 100,000 habitantes |
| `Age Adjusted Rate` | float | Tasa ajustada por edad (para comparabilidad) |

## Códigos ICD-10 usados

- **X60-X84**: Intencional self-harm (suicidio, todas las modalidades)
  - X60: Ingesta de analgésicos no opioides, antipiréticos y antirreumáticos
  - X61: Ingesta de medicamentos antiepilépticos, sedantes, antiparkinsonianos, psicotrópicos
  - X70: Ahorcamiento, estrangulación y sofocación
  - X71: Ahogamiento y sumersión
  - X74: Disparo de arma de fuego
  - X76: Humo, fuego y llamas
  - X78: Objeto cortante
  - X80: Salto desde lugar elevado
  - X81: Saltar o acostarse delante de objeto en movimiento
  - X82: Colisión intencional de vehículo de motor
  - X83-X84: Otros especificados / no especificados
- **X87.0**: Assault by sharp objects (no es suicidio, no lo usamos)

**Filtramos solo X60-X84** para quedarnos con suicidios consumados.

## Limitaciones generales

- **Subregistro.** Las muertes por suicidio están frecuentemente
  sub-reportadas, especialmente en adolescentes. Los médicos forenses
  pueden clasificar intencionalidad dudosa como "accidente".
- **Cambio de sistema de codificación.** En 1999 EE.UU. pasó de ICD-9 a
  ICD-10. La ventana 2005-2020 está enteramente en ICD-10, no es un problema.
- **Agregación.** WONDER solo permite granularidad por año, edad-grupo y
  sexo a nivel nacional. Para análisis a nivel estatal se requiere el
  Restricted-Use Data Agreement (no público).
- **Población subyacente.** WONDER usa estimaciones poblacionales del
  Census Bureau. Pequeñas diferencias con respecto a otras fuentes son
  esperables.

## Por qué combinar YRBS + WONDER

YRBS pregunta a ~13 000 high schoolers por año si **han intentado**
suicidarse. WONDER cuenta **muertes reales** en toda la población (no solo
high school). La tasa de mortalidad de WONDER es una medida de la severidad
del fenómeno; las tasas de intento de YRBS son una medida de prevalencia.
Juntos dan una imagen completa.
