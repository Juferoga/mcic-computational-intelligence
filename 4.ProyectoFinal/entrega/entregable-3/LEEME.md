# Entregable 3 · Riesgo de los commits del kernel de Linux

Juan Felipe Rodríguez Galindo · 20261595004 · Inteligencia Computacional · MCIC-UD

| Archivo | Contenido |
|---|---|
| `*-entregable-3.pdf` | Artículo IEEE con la metodología, la partición temporal, las métricas, las pruebas declaradas y la validación de las referencias. |
| `*-proyecto-e3-cuaderno.ipynb` | Cuaderno ejecutado. Verifica los datos, reserva la prueba de 2026 y reproduce las tablas de partición, preprocesamiento y validación. La sección 8 compara la referencia completa con una variante reducida por correlación. |
| `*-proyecto-e2-cuaderno.ipynb` | Exploración previa citada en el apéndice de reproducibilidad. |
| `registro_experimentos_e3.csv` | 30 entrenamientos en validación, con configuración, semilla, ventana, métricas y tiempo. |
| `*-entregable-3-anexo.xlsx` | Diccionario de variables, matriz del estado del arte y evidencia del análisis de datos. |
| `config/` | Protocolo de evaluación y espacio de hiperparámetros del modelo propuesto. |
| `datos/`, `requirements.txt` | Copia verificable del conjunto de datos y versiones del entorno. |

## Reproducción local

Descomprime el ZIP y ejecuta lo siguiente desde la carpeta `entregable-3`, con Python 3.13:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt jupyter
jupyter lab
```

Abre el cuaderno E3 en JupyterLab y ejecuta todas las celdas. La ejecución regenera el CSV y escribe `resultados_e3.json`. El cuaderno utiliza la semilla 11 para las referencias. El protocolo fija las semillas 11, 23, 37, 41 y 53 para la evaluación de estabilidad posterior.

El cuaderno verifica el SHA-256 de la copia en `datos/`. Si la copia local falta, intenta descargar el [release v1.0 del conjunto de datos](https://github.com/Juferoga/linux-kernel-commits-jit/releases/tag/v1.0). SHA-256: `ac6858f4b16cb9ee4c7fd1f8baf3c28d480a729dbce9829665d9cdc65045fe9e`.

La prueba de enero a julio de 2026 solo se usa para verificar el tamaño y la huella del bloque reservado. Las cifras del artículo y del CSV corresponden a las ventanas de validación de 2023, 2024 y 2025.
