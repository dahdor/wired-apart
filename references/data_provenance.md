# Data Provenance — Wired Apart

> Documento vivo. Cada vez que se descarga o actualiza un dataset crudo, se
> agrega una entrada con fecha, URL, hash y notas. Esto garantiza la
> reproducibilidad bit-a-bit del pipeline.

## Formato de cada entrada

```
## <dataset_name> @ <YYYY-MM-DD HH:MM TZ>

- **URL:** <url de descarga>
- **Archivo local:** <ruta relativa a data/raw/>
- **SHA-256:** <hash>
- **Tamaño:** <bytes>
- **Versión / año de los datos:** <ej. "2023 release">
- **Variables clave mapeadas a nuestro análisis:** <lista>
- **Limitaciones conocidas:** <ej. "NSDUH 2015 redesign">
```

---

## Monitoring the Future (MTF)

> _Pendiente de descarga en Fase 2._

## National Survey on Drug Use and Health (NSDUH)

> _Pendiente de descarga en Fase 2._
