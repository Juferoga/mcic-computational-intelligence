# Clasificador difuso-evolutivo para riesgo de commits del kernel de Linux

Proyecto final de Inteligencia Computacional (MCIC, Universidad Distrital Francisco José de Caldas).
Autor: Juan Felipe Rodríguez Galindo (20261595004).

**Pregunta.** ¿Un clasificador difuso-evolutivo interpretable (≤ 15 reglas, ≤ 3 antecedentes) mantiene su
desempeño al pasar de commits del kernel anteriores a la era de asistentes de IA (2019–2025) a commits de
2026? Se compara con clase mayoritaria, regresión logística, gradient boosting y una variante del modelo
difuso sin evolución.

## Contenido

| Ruta | Qué es |
|---|---|
| `juan-rodriguez-20261595004-proyecto-cuaderno.ipynb` | Cuaderno autocontenido (Colab): verifica la prueba, entrena con la configuración congelada y evalúa una vez. Ejecutado, con salidas. |
| `juan-rodriguez-20261595004-proyecto-registro-experimentos.csv` | Registro de todas las corridas (etapa, modelo, configuración, semilla, ventana, métricas, tiempo, parámetros). |
| `src/` | Código del experimento por etapas (ver abajo). |
| `config/` | Protocolo de evaluación, espacio de hiperparámetros y configuración congelada con la huella SHA-256 de la prueba. |
| `resultados/` | JSON de cada etapa, reglas aprendidas y figuras. |
| `juan-rodriguez-20261595004-proyecto-articulo.pdf` | Artículo IEEE final. |
| `juan-rodriguez-20261595004-proyecto-presentacion.pdf` | Diapositivas de la sustentación. |
| `juan-rodriguez-20261595004-proyecto-anexo-matriz.csv` | Matriz completa del estado del arte (58 trabajos, con la URL verificada). |

## Datos

- Fuente: clon completo de `torvalds/linux` (rama principal, sin merges, desde 2014).
- Tabla procesada: un commit por fila, 2019-01-01 a 2026-11-06. El autor se reemplaza por un identificador
  SHA-256 con sal; no se publican nombres ni correos.
- Etiqueta `riesgoso`: un commit posterior lo cita con `Fixes:` en 90 días o menos. Los commits con menos
  de 90 días de observación quedan marcados `censurado` y no se usan.
- Enlace de descarga de la tabla: ver la primera celda del cuaderno (`URL_DATOS`).

## Entorno

Python 3.13 con las versiones de `requirements.txt`:

```
pandas==3.1.1  scikit-learn==1.9.1  numpy==2.5.4  pyarrow==26.0.1  matplotlib==3.11.2  scipy==1.18.1  joblib==1.6.0
```

```bash
uv venv && uv pip install -r requirements.txt
```

## Semillas y decisiones fijas

- Semillas de entrenamiento: 11, 23, 37, 41, 53. Búsqueda aleatoria: 2026. Bootstrap: 1 (AUC-PR) y 2 (AUC-ROC).
- Partición temporal: entrenamiento desde 2019-01-01; validación con ventana creciente en 2023, 2024 y
  2025 con un hueco de 90 días antes de cada ventana; prueba 2026-01-01 a 2026-07-31.
- Variables del modelo difuso (fijadas antes de ver resultados): `lineas_add`, `lineas_del`, `n_archivos`,
  `n_subsistemas`, `n_reviewed`, `n_signed`, `es_fix`, `cc_stable`, `exp_autor`, `exp_autor_subsistema`.

## Pasos para reproducir

```bash
# 0. (opcional, 30–60 min, 6,5 GB) minar el kernel
git clone --bare https://github.com/torvalds/linux.git ~/datos-kernel/linux.git
python src/minar_kernel.py --repo ~/datos-kernel/linux.git --salida ~/datos-kernel/commits.parquet

# 1. exploración y verificaciones D1–D7             -> resultados/e2/
python src/e2_exploracion.py
# 2. referencias en validación y protocolo          -> resultados/e3/, config/
python src/e3_referencias.py
# 3. búsqueda, sensibilidad, semillas, variante     -> resultados/e4/, config/configuracion_final.json  (~3,5 h, 6 procesos)
python src/e4_busqueda.py --procesos 6
# 4. evaluación única en 2026                        -> resultados/final/
python src/final_prueba.py
# 5. iteración 2 (protocolo fijado en config/protocolo_iteracion2.json) -> resultados/iteracion2/
python src/iteracion2.py --procesos 6     # no se adoptó: la prueba no se volvió a evaluar
# 6. figuras                                         -> resultados/figuras/
python src/figuras.py
```

La ruta de la tabla se cambia con la variable de entorno `DATOS_KERNEL`. `final_prueba.py` se niega a
correr si la huella de la partición de prueba no coincide con la congelada en el paso 3.

## Resultado

El criterio de éxito fijado en la Entrega 1 no se alcanzó (C1: 91,1 % del AUC-PR del gradient boosting,
meta 95 %; C2: el difuso cae 19,5 % frente a 16,3 %; C3 solo en su primera parte). Una segunda
iteración, decidida solo con validación, no superó a la primera y no se evaluó en la prueba. Detalle en el
artículo, secciones V y VI.

## El cuaderno

- `MODO = "RAPIDO"` entrena una semilla por modelo (~5 min en un portátil, más en Colab).
- `MODO = "COMPLETO"` entrena las cinco semillas.
- La celda de comparación muestra que cada AUC-PR coincide con el del artículo (diferencia 0,0).
- El cuaderno se niega a seguir si la huella SHA-256 de la partición de prueba no coincide.
