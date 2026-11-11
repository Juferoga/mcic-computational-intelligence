# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es esta carpeta

Proyecto final de *Inteligencia Computacional* (MCIC, UD, docente César Andrey Perdomo Charry). Equipo de una persona (Juan Felipe Rodríguez Galindo). Todo se escribe en español.

- `Proyecto_final_modelo_de_inteligencia_computacional.pdf`: enunciado oficial (fases CRISP-ML(Q), cronograma, entregables, rúbrica de 100 puntos). Es la fuente de verdad de los requisitos.
- `README.md`: resumen de los lineamientos y las fechas.
- `PLAN.md`: plan de trabajo día a día con las decisiones ya tomadas. Léelo antes de proponer algo. Si una decisión cambia, actualiza `PLAN.md` en lugar de dejarla solo en la conversación.

El plan menciona `count_ai.py` como punto de partida de la minería, pero ese archivo no existe en ninguna parte.

## Estructura y comandos

- `revision/`: la revisión del estado del arte (Fase 1).
  - `protocolo.md`: criterios de inclusión y exclusión, escritos antes del tamizaje. Cualquier cambio se anota ahí con fecha.
  - `busqueda_arxiv.py`: búsqueda real contra la API de arXiv; escribe `resultados/arxiv_Q*.csv` y `resultados/conteos_arxiv.json`.
  - `tamizaje_arxiv.py`: decisiones de tamizaje escritas a mano, cada una con su criterio.
  - `busqueda_openalex.py` y `tamizaje_openalex.py`: segunda base. Reemplaza a IEEE Xplore porque el usuario no tiene acceso; la desviación del enunciado está declarada en `protocolo.md` y en el artículo. Los registros se numeran n=1..195 (Q1 y luego Q2) y las decisiones de texto completo están en `fichas/lote6-9`. No se raspa IEEE con curl: el clasificador de permisos lo bloquea.
  - `fichas/*.json`: un trabajo verificado por elemento (cita IEEE, URL abierta, texto completo o solo resumen, campos de la matriz). `viabilidad.json` documenta la compuerta del 6 de noviembre.
  - `generar_e1.py`: genera `articulo/entregable-1/generado/{conteos,referencias}.tex` y `resultados/matriz_completa.csv`. La bibliografía sale de las fichas en el orden de `\cite` en `main.tex`, y falla si se cita algo sin ficha verificada.
- `articulo/entregable-1/`: IEEEtran más `estilo-mcic.tex`, que solo agrega color UD, figuras TikZ y fuente Times New Roman del manual vía fontspec, porque tectonic es XeTeX.

```bash
cd revision && python3 generar_e1.py                 # después de cualquier cambio en fichas, conteos o citas
cd ../articulo/entregable-1 && tectonic main.tex     # debe dar ≤4 páginas en la Entrega 1
```

- `src/minar_kernel.py` minea un clon bare del kernel, que está en `~/datos-kernel/linux.git` y queda fuera del repo por tamaño, y produce `~/datos-kernel/commits.parquet`: un commit por fila, autor anonimizado, etiqueta `riesgoso` y columna `censurado`. `src/factibilidad.py` escribe `factibilidad/resultados.json` y las figuras. El entorno es `.venv` de esta carpeta (uv), con versiones en `requirements.txt`.
- `entrega/entregable-N/`: exactamente lo que se sube a Classroom, con nombre `juan-rodriguez-20261595004-proyecto-entregable-N*`.

```bash
.venv/bin/python src/minar_kernel.py --repo ~/datos-kernel/linux.git --salida ~/datos-kernel/commits.parquet   # ~30-60 min
.venv/bin/python src/factibilidad.py --datos ~/datos-kernel/commits.parquet
```

Ninguna cifra del artículo se escribe a mano si sale de los datos: los conteos son macros (`\nArxivTotal`, `\nTotalIncluidos`…) y las cifras de la matriz vienen de las fichas. Los marcadores `\pendiente{...}` (en rojo) señalan lo que falta antes de entregar.

### Experimento (etapas, en orden)

`src/comun.py` concentra partición, modelos, métricas y registro; cada etapa lo importa. `e2_exploracion.py` → `e3_referencias.py` (escribe `config/protocolo_evaluacion.json` y `espacio_hiperparametros.json`) → `e4_busqueda.py` (congela `config/configuracion_final.json` con la huella SHA-256 de la prueba) → `final_prueba.py` (evaluación única; guarda los ajustes en `resultados/final/cache_ajustes.joblib`, que no se entrega) → `figuras.py`. La iteración 2 (`config/protocolo_iteracion2.json`, fijado antes de correr) está en `iteracion2.py` y `final_prueba.py --iteracion 2`. Las corridas largas se lanzan con `caffeinate -dimsu` (el Mac se durmió una vez a mitad de E4). En el registro, `FINAL-prueba-intento1` son las filas de una corrida que se cayó en el análisis posterior por un error de índices; la segunda reprodujo las mismas cifras.

### Artículos de las entregas 2–4 y final

Cada entregable es incremental: `articulo/entregable-N/main.tex` reutiliza las secciones del anterior (`seccion-*.tex`) y agrega las suyas.

```bash
.venv/bin/python articulo/generar_cifras.py   # macros \cif... y cuerpos de tabla en articulo/comun/ desde resultados/
cd revision && python3 generar_e1.py N        # bibliografía del entregable N (sigue los \input)
cd ../articulo/entregable-N && tectonic main.tex
```

- Los nombres de macro no pueden llevar dígitos (`\cifRegE3` falla).
- Las filas de tabla generadas se incluyen con `\filas{../comun/tabla_x.tex}` (usa `\@@input`), porque `\input` dentro de un `tabular` rompe `\midrule`.
- Las referencias de metodología están en `revision/fichas/lote10_metodologia.json` con `decision: incluido-metodologia`: entran a la bibliografía pero no al conteo PRISMA.

`cuadernos/construir_cuaderno.py` arma el cuaderno de Colab copiando literalmente `difuso.py` y partes de `comun.py`, incrusta la configuración congelada y exporta la tabla anonimizada a `cuadernos/datos/`. El enlace público de la tabla (`URL_DATOS`) está pendiente de que el autor elija dónde alojarla.

## Proyecto (resumen de PLAN.md)

- **Pregunta:** ¿un clasificador difuso-evolutivo interpretable (≤15 reglas) mantiene su desempeño al pasar de commits del kernel de Linux de la era pre-IA a commits de 2026 (con trailer `Assisted-by`)? Se compara con clase mayoritaria, regresión logística, gradient boosting y una variante del difuso sin evolución.
- **Etiqueta:** el commit es riesgoso si un `Fixes:` posterior lo cita en ≤90 días. Solo entran commits con ≥90 días de observación (censura por la derecha).
- **Datos:** dataset de Zenodo (llega hasta nov 2023, incluye `bfc_bic.csv`) más minería de un clon completo de `torvalds/linux` para 2024–2026. Plan B: AIDev (PRs de agentes) con el mismo pipeline.
- **Métricas:** la principal es AUC-PR; las secundarias, MCC, AUC-ROC, sensibilidad y especificidad. Significancia con McNemar e IC 95 % por bootstrap (Friedman + Nemenyi para varios modelos en varias ventanas). No uses Wilcoxon con 5 semillas.
- **Entregas:** domingos 8, 15, 22 y 29 de nov (PDF IEEE incremental), final el jue 3 dic (artículo IEEE de 8–10 págs., código, registro de experimentos y presentación) y sustentación el vie 4 dic.

## Reglas metodológicas que no se negocian

- **Sin fuga de datos:** solo variables conocidas al momento de integrar el commit. Escalado, imputación, selección y balanceo se ajustan solo con entrenamiento, dentro de un `Pipeline`.
- **División temporal:** se entrena con el pasado y se valida con ventanas móviles; nunca hay mezcla aleatoria.
- **El test de 2026 se mina y se guarda, pero no se toca** hasta la evaluación única (30 nov), y antes se verifica su suma de verificación. Nunca se reajusta nada con el test. Si el modelo difuso pierde, se reporta tal cual.
- **Anonimización:** los nombres y correos de autores se reemplazan por identificadores en toda tabla que se entregue.
- **Semillas fijas** y parámetros (rutas, semillas, umbrales) al inicio del código, nunca en duro en el medio. Cada corrida se registra en `registro_experimentos.csv`.
- **Referencias:** cada cita se verifica (autor, año, medio) abriendo la fuente. Las referencias inexistentes cuentan como insuficientes en la rúbrica.

## Reproducibilidad y empaquetado

- El cuaderno entregado debe correr en una **sesión limpia de Colab**: parte de la tabla ya procesada y anonimizada (con enlace de descarga). La minería del kernel va aparte, como script, y no forma parte del cuaderno.
- Estructura de repositorio que sugiere el enunciado: README (versiones, semillas, pasos), datos, cuadernos, `src`, resultados y artículo.
- Lo que se sube a Classroom debe ser autocontenido: código adjunto y ejecutado con salidas visibles, sin referencias a Makefiles ni a archivos no entregados, sin salidas de otros ejercicios y con nombres de archivo correctos (convención del curso: `juan-rodriguez-20261595004-...`).
- El artículo lleva una sección honesta de **"Declaración de uso de IA"** (herramienta, partes y cómo se verificó), sin meta-texto de formato ni imágenes decorativas. Las conclusiones deben ser hallazgos concretos con cifras propias.
- El alcance se ajusta al enunciado: nada de extras grandes que no se pidieron.

## Entorno y herramientas (heredado del resto del repo)

- La raíz del repo es `..`. El entorno Python es el `.venv` de la raíz; los talleres usan `uv` (`uv venv && uv pip install -r requirements.txt`).
- `pdftotext` no está instalado. Para leer el PDF del enunciado usa la herramienta Read con `pages`.

## Manual de marca UD (`~/repos/ud/maestria/mcic/.UniversidadDistrital-manual-marca`)

El artículo (entregas semanales y final) usa la plantilla **IEEE**, no `ud-informe.sty`. La marca UD aplica sobre todo a la presentación de la sustentación (8–10 diapositivas, 12 min + 5 de preguntas), hecha con el tema Beamer de `plantillas-latex/`. Lee `plantillas-latex/README.md` y `ejemplos/presentacion-ejemplo.tex` antes de armarla.

```bash
UD=$HOME/repos/ud/maestria/mcic/.UniversidadDistrital-manual-marca/plantillas-latex
tectonic -Z search-path=$UD presentacion.tex                                  # compilar
uv run --no-project --with pymupdf python $UD/revisar_pdf.py presentacion.pdf # márgenes y panel de portada
```

- Estructura: `\usetheme{UD}`, `\UDportada{...}`, `\UDCard`, `\UDcierre{...}`. Las columnas van siempre con `[T,onlytextwidth]` y los tamaños de letra con `\fontsize{..}{..}\selectfont`. El panel de la portada deja unos 5,3 × 4,2 cm: parte los títulos largos en dos líneas.
- Paleta (`design.md`): rojo #ED3237, azul #1291C0, dorado #B49739, verde #00A859, plata #98999A, sable #373435. Como el logo MCIC es azul, se usa azul como acento en lugar del rojo de la plantilla. Los logos nunca se recolorean.
- Tipografía: Cambria para títulos, Times New Roman para el texto. Las fuentes se leen de `fuentes/` del manual; no las copies al repositorio (son de Microsoft y el repo es público).
- Al escudo y al logo no se les aplican efectos, animaciones, recortes ni cambios de proporción.
- Evita emojis y glifos de chulo, equis o triángulo; usa palabras (OK, Conservado, Cambiado).
- No hagas commits salvo que el usuario lo pida, y nunca agregues `Co-Authored-By`.
