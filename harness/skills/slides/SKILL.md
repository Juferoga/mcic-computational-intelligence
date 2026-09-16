---
name: mis-presentaciones-pptx
description: "Crea, edita, analiza, convierte y revisa archivos .pptx. Úsala para cualquier tarea relacionada con PowerPoint: crear presentaciones, modificar diapositivas, extraer contenido, corregir diseño, convertir formatos o validar un deck existente."
---

# SKILL: PRESENTACIONES POWERPOINT (.PPTX)

## 0. REGLA PRINCIPAL

Cuando trabajes con un `.pptx`, NO des por terminado el trabajo solo porque el archivo se haya generado sin errores.

El flujo obligatorio es:

**entender → elegir herramienta → crear/editar → guardar → validar estructuralmente → renderizar → revisar visualmente → corregir → volver a validar → entregar.**

La revisión visual es obligatoria. Un `.pptx` que se genera correctamente puede seguir teniendo texto cortado, objetos superpuestos, imágenes deformadas o elementos fuera del lienzo.

---

# 1. IDENTIFICA PRIMERO QUÉ QUIERE EL USUARIO

Clasifica la tarea en una de estas categorías:

### A. Crear una presentación nueva
Usa `pptxgenjs` o `python-pptx`.

### B. Editar una presentación existente
Usa primero `python-pptx`. Si no permite hacer el cambio necesario, considera edición directa del XML.

### C. Leer, resumir o extraer texto
Usa `markitdown`.

### D. Revisar diseño o detectar errores visuales
Convierte el `.pptx` a PDF y después a imágenes. Revisa esas imágenes.

### E. Convertir un archivo antiguo `.ppt`
Usa LibreOffice en modo headless para convertirlo a `.pptx`.

### F. Hacer varias de las anteriores
Combina los pasos anteriores en ese orden y valida al final.

**Nunca elijas una herramienta por costumbre. Elige según la tarea.**

---

# 2. ANTES DE MODIFICAR UN ARCHIVO EXISTENTE

Si el usuario proporcionó un `.pptx` existente:

1. No sobrescribas el original de inmediato.
2. Conserva una copia del archivo de entrada.
3. Identifica número de diapositivas, tamaño del lienzo y contenido.
4. Extrae el texto con `markitdown` cuando sea útil.
5. Haz cambios pequeños y verificables.
6. Guarda el resultado en un archivo de salida separado.
7. Renderiza el resultado antes de entregarlo.

Si el archivo está dañado, no inventes que se pudo editar. Primero intenta una conversión o una reparación compatible y verifica el resultado.

---

# 3. ELECCIÓN DE HERRAMIENTA

| Tarea | Herramienta recomendada |
|---|---|
| Crear deck nuevo | `pptxgenjs` |
| Crear o editar con Python | `python-pptx` |
| Extraer/revisar texto | `markitdown` |
| Convertir `.pptx` → PDF | `soffice --headless --convert-to pdf` |
| PDF → imágenes | `pdftoppm` |
| Convertir `.ppt` → `.pptx` | `soffice --headless --convert-to pptx` |
| Edición avanzada que no resuelve la librería | XML dentro del ZIP del `.pptx` |

### Regla de preferencia

Para un deck nuevo, usa `pptxgenjs` salvo que exista una razón clara para usar `python-pptx`.

Para un deck existente, usa `python-pptx` primero.

No edites XML directamente si la librería ya puede hacer el cambio de forma segura.

---

# 4. CREAR UN PPTX CON PPTXGENJS

## 4.1 Estructura mínima

```js
const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE"; // 13.333 × 7.5 in

const slide = pptx.addSlide();

slide.addText("Título", {
  x: 0.5,
  y: 0.4,
  w: 12.3,
  h: 0.7,
  fontSize: 32,
  bold: true
});

await pptx.writeFile({
  fileName: "salida.pptx"
});
```

## 4.2 Reglas obligatorias

- Define `pptx.layout` ANTES de agregar diapositivas.
- Usa un solo `new pptxgen()` por archivo de salida.
- En colores hexadecimales usa `FF0000`, no `#FF0000`.
- No pongas coordenadas fuera del lienzo.
- Usa `bullet: true` para viñetas; no escribas manualmente `•` salvo que sea texto intencional.
- Las notas del orador van en `slide.addNotes(...)`.
- Usa unidades coherentes: `x`, `y`, `w`, `h` están en pulgadas.
- Antes de generar muchas diapositivas, define un sistema de márgenes y tamaños.
- No copies y pegues layouts sin revisar si el contenido cabe.

## 4.3 Tamaño recomendado para texto

Como regla inicial:

- Título: 32–44 pt.
- Subtítulo: 20–28 pt.
- Texto principal: 16–24 pt.
- Texto secundario: 12–16 pt.
- Pie de página: 9–12 pt.

No reduzcas automáticamente el texto hasta hacerlo ilegible. Primero intenta:
1. eliminar redundancias,
2. dividir el contenido,
3. reorganizar columnas,
4. aumentar la altura disponible,
5. crear otra diapositiva.

---

# 5. CREAR/EDITAR CON PYTHON-PPTX

Ejemplo mínimo:

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

slide = prs.slides.add_slide(prs.slide_layouts[6])

box = slide.shapes.add_textbox(
    Inches(0.5), Inches(0.4), Inches(12.3), Inches(0.8)
)

tf = box.text_frame
p = tf.paragraphs[0]
run = p.add_run()
run.text = "Título"
run.font.size = Pt(36)
run.font.bold = True

prs.save("salida.pptx")
```

## Regla importante

No reemplaces innecesariamente todo `text_frame.text` cuando necesites conservar formato.

Para cambios finos, edita párrafos y `runs` individualmente.

---

# 6. LEER UN PPTX

Usa:

```bash
markitdown archivo.pptx
```

Utiliza la salida para:

- detectar diapositivas vacías,
- verificar que el texto esperado existe,
- resumir contenido,
- comprobar que no desapareció texto después de una edición,
- buscar placeholders.

Busca especialmente:

```text
TODO
TBD
lorem
ipsum
[insertar]
[imagen]
[texto]
```

No concluyas que el contenido visual está correcto solamente porque `markitdown` muestre todo el texto.

---

# 7. REVISIÓN VISUAL OBLIGATORIA

Después de crear o modificar el `.pptx`, ejecuta:

```bash
mkdir -p render
soffice --headless --convert-to pdf --outdir render salida.pptx
pdftoppm -jpeg -r 150 render/salida.pdf render/slide
```

Esto produce imágenes de las diapositivas para inspección.

## Revisa TODAS las diapositivas

No revises solo la portada.

Busca:

### Texto
- texto cortado,
- texto que desborda su caja,
- títulos demasiado largos,
- tamaño ilegible,
- líneas excesivamente apretadas,
- saltos de línea extraños.

### Objetos
- elementos superpuestos,
- imágenes fuera del lienzo,
- formas parcialmente ocultas,
- iconos deformados,
- objetos demasiado cerca entre sí,
- alineaciones incorrectas.

### Diseño
- márgenes inconsistentes,
- contraste insuficiente,
- exceso de elementos,
- espacios vacíos accidentales,
- estilos diferentes sin motivo.

### Contenido
- placeholders,
- diapositivas vacías,
- imágenes faltantes,
- textos duplicados,
- errores de ortografía evidentes introducidos durante la generación.

---

# 8. REGLAS DE LAYOUT

## Márgenes

Como punto de partida, deja aproximadamente `0.5 in` o más respecto al borde cuando el diseño lo permita.

No acerques elementos innecesariamente al límite del lienzo.

## Separación

Evita elementos pegados entre sí. Como referencia, deja alrededor de `0.2–0.3 in` entre bloques independientes cuando el diseño lo permita.

## Alineación

Alinea elementos por:

- borde izquierdo,
- borde derecho,
- eje central,
- o retícula.

No coloques objetos “a ojo” si varios elementos deberían compartir una alineación.

## Una idea por diapositiva

Cada diapositiva debe tener una función clara.

Si hay demasiado contenido:

**divide la diapositiva** en lugar de reducir el texto hasta hacerlo difícil de leer.

---

# 9. DISEÑO VISUAL

Usa un sistema consistente:

- 1 color dominante.
- 1–2 colores de apoyo.
- 1 color de acento.
- 1–2 familias tipográficas como máximo.
- Espaciado consistente.
- Componentes repetidos con las mismas dimensiones.

No hagas que todas las diapositivas tengan exactamente la misma composición.

Puedes variar entre:

- dos columnas,
- cuadrícula 2×2,
- imagen + texto,
- comparación,
- cifras grandes,
- cronología,
- proceso,
- cita,
- cierre.

Pero la identidad visual debe permanecer consistente.

## Contraste

Nunca uses texto claro sobre fondo claro o texto oscuro sobre fondo oscuro sin suficiente contraste.

## Elementos visuales

Cuando la diapositiva lo requiera, utiliza al menos un recurso visual pertinente:

- imagen,
- gráfico,
- icono,
- forma,
- diagrama,
- cifra destacada.

No añadas elementos decorativos sin función.

---

# 10. IMÁGENES

Al insertar imágenes:

1. Verifica que el archivo exista.
2. Comprueba sus dimensiones.
3. Mantén su proporción.
4. Evita estirar una imagen solo para llenar un espacio.
5. Si la imagen debe ocupar una región fija, recórtala proporcionalmente.
6. Comprueba visualmente el resultado renderizado.

Nunca asumas que una imagen se ve bien solo porque el archivo se insertó correctamente.

---

# 11. TABLAS Y GRÁFICOS

Para tablas:

- evita meter demasiadas columnas,
- usa encabezados claramente diferenciados,
- mantén texto legible,
- alinea datos numéricos cuando corresponda.

Para gráficos:

- usa títulos claros,
- etiqueta unidades,
- evita elementos redundantes,
- no dependas únicamente del color para comunicar información.

Una tabla ilegible no se considera correcta aunque técnicamente esté dentro del lienzo.

---

# 12. EDICIÓN DIRECTA DEL XML

Solo usar cuando `python-pptx`/`pptxgenjs` no permitan realizar el cambio necesario.

Recuerda:

- `.pptx` es un ZIP con XML.
- El contenido de las diapositivas está bajo `ppt/slides/`.
- Respeta namespaces XML.
- Usa `lxml` u otra herramienta XML apropiada.
- Haz copia de seguridad antes de modificar.
- Reempaqueta correctamente la estructura.
- Después de editar XML, abre/renderiza el `.pptx` para comprobar que no quedó corrupto.

Nunca cambies texto XML mediante reemplazos ciegos si puede romper relaciones, namespaces o caracteres especiales.

---

# 13. ERRORES Y RECUPERACIÓN

Si una herramienta falla:

### Si falla `markitdown`
Prueba una extracción alternativa o inspecciona el deck directamente con la librería de PowerPoint.

### Si falla `soffice`
Comprueba:
- que el archivo exista,
- que el formato sea válido,
- que LibreOffice esté instalado,
- que el directorio de salida exista.

### Si `pdftoppm` falla
Comprueba primero que el PDF realmente fue generado.

### Si el PPTX está corrupto
No lo entregues. Intenta:
1. abrirlo/convertirlo con LibreOffice,
2. reconstruir el deck con una librería,
3. reparar XML solamente si es necesario,
4. volver a validarlo.

### Si el resultado tiene overflow
No lo “dejes pasar”. Corrige el layout y vuelve a renderizar.

---

# 14. VALIDACIÓN FINAL OBLIGATORIA

Antes de entregar un `.pptx`, comprueba TODO esto:

## Validación estructural

- [ ] El archivo existe.
- [ ] Se puede abrir/convertir sin marcar corrupción.
- [ ] Tiene el número esperado de diapositivas.
- [ ] El texto importante sigue presente.
- [ ] No hay `TODO`, `TBD`, `lorem`, `[insertar]` ni placeholders accidentales.

## Validación visual

- [ ] Se revisaron todas las diapositivas renderizadas.
- [ ] No hay texto cortado.
- [ ] No hay objetos superpuestos.
- [ ] No hay elementos fuera del lienzo.
- [ ] Las imágenes mantienen proporción.
- [ ] El contraste es suficiente.
- [ ] Los márgenes y alineaciones son coherentes.
- [ ] No hay diapositivas accidentalmente vacías.
- [ ] El diseño es consistente.

## Regla de cierre

**Si una de estas comprobaciones falla, NO entregues todavía. Corrige y vuelve a validar.**

---

# 15. ORDEN EXACTO RECOMENDADO

Cuando tengas que resolver una tarea completa, sigue este orden:

```text
1. Leer la solicitud.
2. Identificar si es crear, editar, analizar o convertir.
3. Identificar si existe un archivo de entrada.
4. Elegir la herramienta.
5. Inspeccionar el archivo existente, si lo hay.
6. Crear o modificar el PPTX.
7. Guardar como archivo de salida.
8. Ejecutar validación estructural.
9. Convertir a PDF.
10. Convertir PDF a imágenes.
11. Revisar TODAS las imágenes.
12. Corregir errores.
13. Repetir pasos 7–12 si hubo cambios.
14. Ejecutar validación final.
15. Entregar únicamente cuando el resultado pase las comprobaciones.
```

---

# 16. PRINCIPIOS PARA UNA IA QUE COMETE ERRORES

Cuando una instrucción sea ambigua:

- No inventes datos importantes.
- Conserva el contenido proporcionado por el usuario.
- Si falta un dato esencial, usa un valor razonable solo cuando no cambie el significado; de lo contrario, pide el dato.
- No elimines información para “hacer que quepa” sin una razón clara.
- No afirmes que revisaste visualmente algo si no lo renderizaste.
- No afirmes que un archivo funciona si no se validó.
- No afirmes que una diapositiva está correcta solo porque el código terminó sin error.
- Prioriza primero **legibilidad y corrección**, después decoración.

## Regla de oro

**Generar el archivo NO es terminar. Validar el archivo sí.**
