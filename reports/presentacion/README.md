# Presentación — *Wired Apart*

Presentación HTML 1920×1080, exportable a PDF como si fuera PowerPoint.
Estructura autocontenida: HTML + CSS + assets locales.

## Estructura

```
presentacion/
├── index.html              ← archivo principal (abrir con Chrome/Edge)
├── styles.css              ← design system + print rules
├── kids2008.jpg            ← portada · infancia 2008
├── teen2018.png            ← portada · adolescencia 2018
├── unimet.png              ← logo Universidad Metropolitana
└── figures/                ← gráficos del análisis
    ├── fig1_sad_hopeless_trend.png
    ├── fig2_sex_gap.png
    ├── fig5_screen_sad_2019.png
    ├── fig9_depression_vs_mortality.png
    └── fig10_forest_or.png
```

## Cómo previsualizar (sin exportar)

1. Abre `index.html` directamente en Chrome/Edge (doble clic).
2. Navega con:
   - **→ / Espacio / AvPág** — siguiente slide
   - **← / RePág** — slide anterior
   - **Inicio / Fin** — ir al primero/último
   - Botones flotantes (esquina inferior derecha)

> Tip: en Chrome/Edge puedes usar **F11** para pantalla completa.

## Cómo exportar a PDF (1920×1080 por slide)

1. Abre `index.html` en **Chrome** o **Edge** (no Firefox — no respeta `@page size`).
2. Pulsa **Ctrl + P** (o usa el botón de imprimir en la HUD inferior derecha).
3. En el diálogo de impresión:
   - **Destino:** "Guardar como PDF"
   - **Márgenes:** "Ninguno"
   - **Tamaño de papel:** debería detectar "20.32 × 11.43 cm" (1920×1080 px a 96 dpi) automáticamente.
   - **Gráficos de fondo:** activado ✅ (es necesario para los colores y degradados).
4. Pulsa **Guardar**.

> Si el tamaño de página no aparece correcto, en el diálogo de impresión
> elige "Personalizado…" e introduce **1920 × 1080 px** (o **20.32 × 11.43 cm**).

## Sistema de diseño

Aplicado según principios UI/UX de manera ligera:

- **Paleta** del proyecto (`config.py`): primary `#1f3a5f`, secondary `#c8462b`,
  accent `#7a9e7e`, highlight `#f4b400`.
- **Tipografía:** Playfair Display (titulares, contraste editorial) + Inter (cuerpo).
- **Espaciado:** ritmo 4/8 pt (`--s-1` a `--s-10`).
- **Contraste:** ≥ 4.5:1 en todos los textos (WCAG AA).
- **Sin emojis** como iconos — todos los iconos son SVG inline.
- **Ratio:** 16:9 nativo (1920×1080), escalable en pantallas menores.

## Slides (alineadas con `script.md`)

| #  | Título                       | Figura                          | Sección            |
| -- | ---------------------------- | ------------------------------- | ------------------ |
| 01 | Portada                      | kids2008 + teen2018             | —                  |
| 02 | La Epidemia Silenciosa       | fig1 (tendencia 2005-2021)      | 01 · Contexto      |
| 03 | La Brecha de Género          | fig2 (sex gap)                  | 02 · Contraste     |
| 04 | La Paradoja                  | fig9 (depresión vs mortalidad)  | 03 · Intersección  |
| 05 | La Curva en J                | fig5 (screen time vs sad)       | 04 · Causa raíz    |
| 06 | Rigor Metodológico           | fig10 (forest OR)               | 05 · Rigor         |
| 07 | Phone-Free Schools           | (4 palancas + KPIs)             | 06 · Solución      |
| 08 | Cierre · "La decisión es…"   | unimet                          | 07 · Cierre        |

## Tiempo estimado de exposición

8:30 min (alineado con el guion en `../script.md`).
