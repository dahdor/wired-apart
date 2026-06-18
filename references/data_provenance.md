# Data Provenance — Wired Apart
_Last updated: 2026-06-18_

## CDC YRBS (Youth Risk Behavior Surveillance System)

**Base URL:** https://www.cdc.gov/yrbs/data/index.html
**Format:** Microsoft Access (`.mdb`), with codebook PDFs.
**Coverage downloaded:** 9 waves (2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2021).

### Variable mapping (Q-codes rotan cada 2 años)

| Concepto | 2005-2009 | 2011 | 2013-2015 | 2017-2021 |
|---|---|---|---|---|
| sad/hopeless | Q23 | Q24 | Q26 | Q25 |
| considered_suicide | Q24 | Q25 | Q27 | Q26 |
| made_plan | Q25 | Q26 | Q28 | Q27 |
| attempted_suicide (bin) | Q22 | Q27 | Q29 (ord) | Q28 |
| attempted_suicide (ord) | — | — | Q29 | — |
| screen_time (Q80) | ❌ no existe | ❌ TV only | ❌ no existe | ✅ **2019 only** (social media + games) |

**No** todos los años tienen screen time en Q80. La métrica moderna de Haidt
(redes sociales + video + games) **solo existe en 2019**. Los demás años
miden actividad física, TV, o deportes.

### yrbs2005.mdb

- **URL:** https://www.cdc.gov/yrbs/files/2005/yrbs2005.zip
- **Local path:** `data/raw/yrbs/yrbs2005.mdb`
- **SHA-256:** `efe195059a396f11655446242d676a00eddc1ffe667329d8abae2b1183c5cad9`
- **Size:** 11.3 MB
- **Codebook:** `data/raw/yrbs/2005_codebook.pdf` (SHA-256: `23702d3ec472bcb92b57fbf77d8beac87447a6b363f25f37dfd811e370c6d2eb`)
- **License:** Public domain (US Government work)

### yrbs2007.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2007/yrbs2007.zip
- **Local path:** `data/raw/yrbs/yrbs2007.mdb`
- **SHA-256:** `2fefb8e23df170ea8e6b49a2dea3e01341345a4b3207e16accd34b2f196ec441`
- **Size:** 19.3 MB
- **Codebook:** `data/raw/yrbs/2007_codebook.pdf` (SHA-256: `777b21d52babba0909b60f98cb14f9c95d26d18f72c247b92b31cd7ba62545cc`)

### yrbs2009.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2009/yrbs2009.zip
- **Local path:** `data/raw/yrbs/yrbs2009.mdb`
- **SHA-256:** `cc3b358db3e962aab96847c13656d187a297ccda42868daed3f115560ccb41fb`
- **Size:** 45.0 MB
- **Codebook:** `data/raw/yrbs/2009_codebook.pdf` (SHA-256: `28b3c808589137b9b2a34124023dbf0ea3261e9e4cea74680cc7a6c0416137fa`)

### yrbs2011.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2011/yrbs2011.zip
- **Local path:** `data/raw/yrbs/yrbs2011.mdb`
- **SHA-256:** `e66538f4a05dfcc985b5c7f52cecb7b1de9f926cfbb7ab3e602e2c0e027bdbb3`
- **Size:** 21.3 MB
- **Codebook:** `data/raw/yrbs/2011_codebook.pdf` (SHA-256: `1f2f7f8212d5a3f137d8ece86b0ac85732da37855c0337a63ea652bd58b07fe8`)

### yrbs2013.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2013/YRBS2013.zip
- **Local path:** `data/raw/yrbs/yrbs2013.mdb`
- **SHA-256:** `1ac5da17ce1b94ba2b46826ee82bbe7a45d29b978e772ad1b32773d5d6e8128a`
- **Size:** 25.5 MB
- **Codebook:** `data/raw/yrbs/2013_codebook.pdf` (SHA-256: `2cc1f2a95809f99057923fac9facf6c7d886f4af9ccca354000e42f60185300f`)

### yrbs2015.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2015/yrbs2015.zip
- **Local path:** `data/raw/yrbs/yrbs2015.mdb`
- **SHA-256:** `28088e68ec6ac9ed8123d50c2055fcfe39d65babf8ac6d6facda49928e4fcbf8`
- **Size:** 50.7 MB
- **Codebook:** `data/raw/yrbs/2015_codebook.pdf` (SHA-256: `0c8edc98ccad82322b33a75a3d0ab6b31f84a3b1c07e53c32349d29e6266a1bd`)

### yrbs2017.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2017/XXH2017_YRBS_Data.zip
- **Local path:** `data/raw/yrbs/yrbs2017.mdb`
- **SHA-256:** `e28c6b56174e0bb8d37bec96afcc43dc819f35f8aea9b7ab4064e79defb37c4c`
- **Size:** 47.9 MB
- **Codebook:** `data/raw/yrbs/2017_codebook.pdf` (SHA-256: `3ac5a8b3e62cef9007c5c86f4b8a6eaba15ebd82ef77332335e6670e5387370a`)

### yrbs2019.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2019/XXH2019_YRBS_Data.zip
- **Local path:** `data/raw/yrbs/yrbs2019.mdb`
- **SHA-256:** `beae213846795bd6cc8961d1517243ac9a11384239ed00a0e6f909641c7ced65`
- **Size:** 25.8 MB
- **Codebook:** `data/raw/yrbs/2019_codebook.pdf` (SHA-256: `b60d9e9571939a47fab597448cda537e12e8c712cd20cd332d2ebe6c0fcd25b1`)

### yrbs2021.mdb
- **URL:** https://www.cdc.gov/yrbs/files/2021/XXH2021_YRBS_Data.zip
- **Local path:** `data/raw/yrbs/yrbs2021.mdb`
- **SHA-256:** `8ed22a313eeec272998d76e45d5b4c1b4f375809db5a2b5ef97b8936dbb37645`
- **Size:** 32.2 MB
- **Codebook:** `data/raw/yrbs/2021_codebook.pdf` (SHA-256: `e758264daa61b0e8750401f98c7485ed98eb21983afa87b7fe5f32aa50e2cfe2`)

## NCHS Suicide Death Rates (data.cdc.gov Socrata API)

**URL:** https://data.cdc.gov/resource/w26f-tf3h.json
**Dataset ID:** `w26f-tf3h`
**Coverage retrieved:** 2018-2024
**Filter applied:** `topic='Suicides' AND 'group'='Sex and age group'`
**Retrieved at:** 2026-06-18
**Output:** `data/processed/wonder_suicide_adolescent_2018_2024.csv` (28 rows)
**SHA-256:** `9d93f45224c30b02e0aa4d25685e8b9150a274be1417b613da511fa0ccca6f03` (wonder_clean_2005_2024.csv, after HUS augmentation)

## NCHS Health, United States 2018, Table 9 (PDF)

**URL:** https://www.cdc.gov/nchs/data/hus/2018/009.pdf
**Format:** PDF (tabla de tasas crudas por 100k, muertes por suicidio, por sexo, edad y año)
**Local path:** `data/external/hus2018_table9.pdf`
**SHA-256:** `646ffd4a1354b7c959ae1651ebb03d80dcd44fc02ec488464007ca5fd46dac05`
**Coverage extracted:** 2010, 2016, 2017 (4 grupos demográficos c/u = 12 filas)
**License:** Public domain (US Government work)
**Uso:** extender la serie de mortalidad hacia atrás de 2018 (límite de Socrata) a 2010.

## NCHS Data Brief 471 (PDF)

**URL:** https://www.cdc.gov/nchs/data/databriefs/db471.pdf
**Format:** PDF (Data Brief sobre suicidio y homicidio en 10-24 años, 2000-2021)
**Local path:** `data/external/db471.pdf`
**SHA-256:** `a8948f5da31f600cd000f44465b4884622b42076009ba9311af85f11a5486e0e`
**Uso:** referencia cualitativa. Los valores de mortalidad adolescente agregada
(ambos sexos, todas las razas, 15-19 años) que se usan en la Fig 13 del
informe se leen de la Figura 1 de este Data Brief. **No son datos
automatizables** (es lectura humana de un PDF).

## Limitación de cobertura 2005-2009 y 2011-2015

El CDC WONDER API (D76, D77, D158, D176) **rechaza todas las queries programáticas** con HTTP 400 "intermittent error" desde este entorno, lo que impide la automatización de la descarga 2005-2017.

**Workaround aplicado:** combinación de NCHS Socrata (2018-2024) + HUS 2018 Table 9 (2010, 2016, 2017).
**Gap restante:** 2005-2009 y 2011-2015. Documentado en el informe (sección Limitaciones) con interpolación explícita entre puntos disponibles (línea punteada en el gráfico de tendencia).

**Output limpio:** `data/processed/wonder_clean_2005_2024.csv` (40 filas: 12 HUS + 28 Socrata, 9 columnas).
