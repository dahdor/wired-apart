# data/interim/

Datos intermedios: cada paso de la limpieza produce un artefacto aquí con
un sufijo de timestamp o número de paso. Permite **auditar** el proceso de
limpieza sin tener que re-ejecutar todo el pipeline.

**Ejemplo:**
```
data/interim/
├── mtf_step1_types.csv
├── mtf_step2_categories.csv
├── mtf_step3_impossible.csv
└── mtf_step7_missing.csv
```

## Política de versionado

Igual que `data/raw/`: no se commitean a git. Se regeneran desde los notebooks
de la Fase 3.
