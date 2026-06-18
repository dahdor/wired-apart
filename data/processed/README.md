# data/processed/

Datasets limpios **finales**, listos para EDA y análisis. Aquí es donde los
notebooks de Fase 3 (`1.0-dh-mtf-cleaning.ipynb`, `1.1-dh-nsduh-cleaning.ipynb`)
escriben su output.

**Archivos canónicos:**
```
data/processed/
├── mtf_clean.csv
├── mtf_clean.parquet       (alternativa binaria, más rápida)
├── nsduh_clean.csv
└── nsduh_clean.parquet
```

## Política de versionado

CSV pequeños (<10 MB) se commitean a git para que el pipeline sea
re-ejecutable sin depender de descargas externas. Archivos grandes (parquet
con todas las variables NSDUH) se regeneran localmente con `make pipeline`.
