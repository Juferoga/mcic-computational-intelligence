# Charla con el profesor: reenvío del Entregable 2

## Antes de clase (sin esto no muestres el PDF)

- [ ] Escribir la declaración de IA con tus palabras en `articulo/entregable-2-corregido/declaracion-ia.tex`. Hoy el PDF muestra en rojo **BORRADOR** y **[versión]** de Gemini.
- [ ] Decidir el umbral de C1. El PDF dice 90 % y el protocolo (`config/protocolo_evaluacion.json`) dice 95 %. Recomendado: poner 95 %.
- [ ] Recompilar, copiar el PDF y regenerar el zip:
  ```
  cd articulo/entregable-2-corregido && tectonic -X compile main.tex \
    && cp main.pdf ../../entrega/entregable-2-corregido/juan-rodriguez-20261595004-proyecto-entregable-2.pdf \
    && cd ../../entrega && rm -f juan-rodriguez-20261595004-proyecto-entregable-2-corregido.zip \
    && zip -rq juan-rodriguez-20261595004-proyecto-entregable-2-corregido.zip entregable-2-corregido
  ```
- [ ] Llevar abiertos el PDF (en la tabla "Seguimiento de los comentarios"), el cuaderno y el Excel.

## 1. Pedir permiso (10 segundos)

> "Profe, revisé su retroalimentación del Entregable 2 y tiene razón en lo que señaló. ¿Me permite reenviarlo corregido por el link de Classroom para que lo revise?"

El 17 de noviembre él dijo que no recalifica después de la retroalimentación y que todo va por Classroom. Por eso pide **permiso para reenviar**. No pidas que te suba la nota.

## 2. Qué fallé (dilo tú, corto)

1. **No adjunté el código**, solo el PDF. Ese fue el criterio 5, "Insuficiente".
2. **No seguí su plantilla del Entregable 2**: la ficha de datos, la tabla D1–D7 con la columna "¿Cumple?", los descriptivos, las figuras y la partición prevista.
3. **Miré la prevalencia del bloque de prueba (2026)** en la exploración. Eso es asomarse a la prueba.
4. **Faltaba el anexo**: el diccionario de variables y la matriz completa en Excel.
5. Arrastraba pendientes del E1:
   - la cifra 31 frente a 37;
   - D3 (backports);
   - los parámetros y el presupuesto del evolutivo;
   - las fechas de las consultas;
   - el DOI de la referencia [32] y el enlace de cada referencia.

## 3. Qué traigo (muéstralo en este orden)

1. **PDF, tabla "Seguimiento de los comentarios"** (al final). Cada comentario suyo aparece con el lugar donde quedó resuelto. Empieza por aquí.
2. **Cuaderno ejecutado**, con las salidas visibles. Primero aparta el bloque de prueba y después explora solo 2019–2025.
3. **Excel del anexo**: diccionario, matriz de 58 trabajos y 43 referencias con DOI o enlace, además de descriptivos, correlaciones, D1–D7, cherry-picks y presupuesto.
4. **Código** en `src/`, con `requirements.txt` y los datos, para que lo pueda correr.

## 4. Lo que encontré al corregir (es tu mejor carta)

- **D3:** en el E2 decía que no había duplicados, y sí los hay. Son **2.305 pares de cherry-picks** (0,41 % del desarrollo, casi todos de `drivers/gpu/drm`). La mediana entre las dos copias es de 3 días y 78 pares tienen etiqueta distinta. Decidí conservar ambas copias y lo justifiqué.
- **El 31 / 37:** el artículo cita 31 de los 58 estudios incluidos; los 58 están en la matriz. El 37 es otra cifra: los incluidos que salieron de las bases en el PRISMA.
- **Presupuesto del evolutivo:**
  - el individuo tiene 150 genes, de los cuales 45 son reales;
  - cada entrenamiento hace hasta 11.280 evaluaciones;
  - un entrenamiento con la configuración máxima tarda 284 s medidos;
  - las 84 corridas previstas suman como máximo unas 6,6 h en un núcleo.

## 5. Si pregunta por el uso de IA

Sé directo y di lo mismo que dice la declaración: qué herramienta usaste, para qué partes y cómo lo verificaste. Ejemplos de verificación:
- ejecutaste el cuaderno completo;
- las cifras salen del código y no están copiadas a mano;
- revisaste cada DOI.

No lo minimices: si él cruza la declaración con lo que digas, tiene que coincidir.

## 6. ¿Le cuento lo de los videos?

**Hoy no lo abras tú.** La conversación de hoy es el E2, y la evidencia de este entregable es el código ejecutable y la tabla de seguimiento.
- **Si él menciona la IA o el proceso:** "En los talleres 1 y 5 grabé el proceso (code-with-me) y lo puedo seguir haciendo en los entregables que faltan".
- **El descuento del 20 % en Deep Learning** es otra conversación, con su propia evidencia (git y videos). No la mezcles hoy.

## 7. Cierre

> "Lo subo hoy por el link de Classroom. Con esto quedo al día y ya arranco el Entregable 3, que va con el pipeline de sklearn."
