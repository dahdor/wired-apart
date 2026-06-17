# Data Dictionary — Monitoring the Future (MTF)

> _Pendiente de redacción en Fase 2, después de descargar el dataset._

## Descripción general

MTF es una encuesta anual de la Universidad de Michigan / NIDA que sigue
muestras representativas nacionalmente de estudiantes de 8°, 10° y 12° grado
en EE.UU. desde 1975. Cuestiona sobre valores, conductas, uso de sustancias y
salud mental percibida.

## Variables de interés para este proyecto

| Variable MTF | Nombre en dataset | Tipo | Rango / valores | Uso en el análisis |
|---|---|---|---|---|
| Año de encuesta | `year` | int | 2005-2020 | Línea temporal principal |
| Grado | `grade` | int (8/10/12) | — | Segmentación |
| Sexo | `sex` | str (male/female) | — | Segmentación por género |
| Satisfacción con uno mismo | `self_satisfaction` | int (1-5) | — | Variable Y de bienestar |
| Soledad | `loneliness` | int (1-5) | — | Variable Y de bienestar |
| Horas de sueño | `sleep_hours` | float | 0-12 | Variable Y de bienestar |
| "Casi a diario" con amigos | `friend_frequency` | bool/cat | yes/no | Variable Y de socialización |
| Horas de pantalla/día | `screen_hours` | float | 0-16+ | Variable X de exposición |

## Pesos muestrales

MTF publica pesos de survey (`weight`) que deben usarse para reproducir las
cifras oficiales. Documentar si el subset descargado los incluye.

## Notas de calidad

- Algunas preguntas rotan o cambian de redacción entre años. Documentar los
  cambios de variable relevantes.
- Celdas con valores especiales (e.g., `*`, `.`, `99`) deben mapearse a NaN
  en la limpieza con justificación explícita.
