# Data Dictionary — National Survey on Drug Use and Health (NSDUH)

> _Pendiente de redacción en Fase 2, después de descargar el dataset._

## Descripción general

NSDUH es una encuesta anual nacional de SAMHSA que entrevista a civiles no
institucionalizados de 12+ años en EE.UU. Cubre uso de sustancias, salud
mental (incluyendo módulos específicos de depresión mayor y ansiedad) y
acceso a tratamiento.

## Variables de interés para este proyecto

| Variable NSDUH | Nombre en dataset | Tipo | Rango / valores | Uso en el análisis |
|---|---|---|---|---|
| Año de encuesta | `year` | int | 2005-2020 | Línea temporal principal |
| Edad | `age` | int (12+) | 12-17 para adolescentes | Segmentación |
| Sexo | `sex` | str (male/female) | — | Segmentación por género |
| Major Depressive Episode (MDE) en último año | `mde_past_year` | bool | 0/1 | Variable Y clínica (la de la Figura 1.1 del libro) |
| Ansiedad | `anxiety_past_year` | bool | 0/1 | Variable Y clínica complementaria |
| Peso muestral | `weight` | float | — | Necesario para cifras oficiales |

## Rediseño metodológico de 2015 — IMPORTANTE

En 2015 SAMHSA rediseñó:
- El instrumento (algunas preguntas cambiaron de redacción).
- El sistema de pesos (de "annual" a "quarterly + annual").
- El método de selección de hogares.

**Implicación para nuestro análisis.** El cambio metodológico puede producir
saltos espurios en las series. Recomendamos:
1. Reportar el cambio explícitamente en el informe.
2. Hacer análisis de sensibilidad excluyendo 2015.
3. Tratar 2015 como punto de segmentación (pre/rediseño/post).

## Pesos muestrales

Imprescindibles para reproducir las cifras oficiales. Documentar la variable
exacta del subset descargado.
