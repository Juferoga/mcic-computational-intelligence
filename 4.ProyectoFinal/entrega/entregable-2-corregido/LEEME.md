# Entregable 2 (versión corregida): datos y modelos

Juan Felipe Rodríguez Galindo, 20261595004. Inteligencia Computacional, MCIC-UD.

| Archivo | Qué es |
|---|---|
| `juan-rodriguez-20261595004-proyecto-entregable-2.pdf` | Artículo (plantilla IEEE del curso) |
| `juan-rodriguez-20261595004-proyecto-entregable-2-cuaderno.ipynb` | Cuaderno autocontenido, **ejecutado** (salidas visibles). Reproduce D1–D7, descriptivos, correlaciones y figuras |
| `juan-rodriguez-20261595004-proyecto-entregable-2-anexo.xlsx` | Anexo: diccionario de variables (Tabla A1), matriz completa del estado del arte (58 trabajos), referencias con DOI/enlace, descriptivos, correlaciones, D1–D7, *cherry-picks* y presupuesto |
| `datos/…parquet` | Tabla anonimizada de commits 2019–2026 (autores con SHA-256 con sal) |
| `src/` | Código: minería del clon (`minar_kernel.py`), exploración (`e2_exploracion.py`), *cherry-picks* (`e2_backports.py`), presupuesto (`e2_presupuesto.py`), anexo (`e2_anexo.py`), partición y modelos (`comun.py`, `difuso.py`) |
| `revision/` | Búsqueda y tamizaje en arXiv y OpenAlex, con las respuestas crudas y las fichas |

## Reproducir

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt jupyter
jupyter nbconvert --to notebook --execute --inplace juan-rodriguez-20261595004-proyecto-entregable-2-cuaderno.ipynb
```

El cuaderno solo necesita `datos/`. Los scripts de `src/` trabajan sobre la tabla completa
minada desde 2014 (`DATOS_KERNEL=…/commits.parquet`) y `e2_backports.py` sobre el clon del kernel
(`KERNEL_GIT=…/linux.git`, `git clone --bare https://github.com/torvalds/linux`).

La exploración usa solo 2019–2025: de 2026 (prueba) solo se cuenta el número de commits.
