# Taller 2 – Series de tiempo: modelos clásicos vs. redes NAR/NARX

Cesar Andrey Perdomo Charry · 50 puntos · Fecha límite: 11 nov.
(En el repo es el Taller 6.)

Adjunto dos plantillas equivalentes:

- `TallerST_Plantilla.ipynb`, para Python en Google Colab.
- `TallerST_Plantilla.m`, para MATLAB.

Entorno en CPU. Abrir el `.m` en una carpeta de trabajo.

En la sección 0 (Configuración), elegir `DATASET`: "appliances", "beijing" o "jena". Para un dataset propio o de interés enviar comentario para analizar si tienes suficientes datos.

Ejecutar todo una vez sin cambios. La plantilla descarga los datos, los valida, hace el diagnóstico y corre el modelo ingenuo estacional.

(marcado como TODO-EQUIPO en el código)

- `modelo_clasico`: SARIMA/SARIMAX u otro modelo clásico justificado. En MATLAB, usen `regARIMA` si incluyen variables exógenas.
- `modelo_neuronal`: red NAR o NARX, con escalado ajustado solo con los datos de entrenamiento.
- `REJILLAS` (sección de sensibilidad): mínimo 2 hiperparámetros × 3 niveles, con al menos 3 semillas.

No modifiquen el motor de evaluación. La prueba externa se ejecuta una sola vez, al final.

Entrega:

- Informe, de 6 a 8 páginas.
- Cuaderno o script ejecutado, con las salidas visibles y la carpeta `resultados/`.

## Material de apoyo

- `propuesto/TallerST_Plantilla.ipynb`: plantilla Python (la que se desarrolla).
- `solucion-profesor/Taller1_SeriesTiempo_Clasicos_vs_NARX.ipynb`: Taller 1 de series, resuelto en clase (serie sintética). "Solo se debe variar lo del bloque 0".
- `SeriesTiempo.pdf`: diapositivas de la sesión (diap. 28: mínimos del Taller 2 — origen móvil ≥ 5 pliegues, sensibilidad ≥ 2 hiperparámetros, Diebold-Mariano, residuos; informe de 6–8 páginas).

Decisiones (2026-11-04): solo Python (no hay MATLAB en este computador), dataset `beijing`, rotulado **Taller 6**, informe con la plantilla UD.
