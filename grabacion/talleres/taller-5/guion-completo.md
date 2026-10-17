# Guion completo · Code with me #2 — Taller 5: Lógica difusa

Ábrelo en VS Code en la **pantalla del MacBook** (OBS solo graba el Samsung): ⌘⇧V muestra la vista previa.

**Cómo leer este guion**
- 🎙 **Di**: lo que hablas (son ideas, no lo leas palabra por palabra).
- ⌨️ **Escribe**: el código que va en la celda del TODO o el comando de la terminal.
- ▶️ **Ejecuta**: Shift+Enter en Jupyter.
- 👀 **Debe salir**: así sabes que vas bien.
- ✅ **Termina**: ⌘⇧→ (marca la tarea en el panel).

Este taller es distinto al 1: **el profe ya dejó el cuaderno escrito** y tú completas 6 `TODO`. Cada TODO tiene un **punto de control** que imprime `[OK]` o `[REVISAR]`. Si sale `[REVISAR]`, no pares: lee la pista en voz alta y corrige.

Fecha límite: **20 de octubre, 11:59 p.m.** Alcance: **solo la parte Python** (no hay MATLAB en este computador; se declara en el informe).

---

## 0. Antes de grabar (sin cámara)

1. Escena del Taller 5 (ya está lista; esto solo la confirma):
   ```bash
   cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/grabacion
   cp talleres/taller-5/tareas.md tareas.md
   cp talleres/taller-5/taller.json overlay/taller.json
   printf 'inicio,fin,duracion_s,fuente\n' > registro_claude.csv
   ```
2. Carpeta del taller limpia:
   ```bash
   cd ../2.Talleres/5.Taller && ls
   ```
   👀 Debe salir solo `bibliografia`.
3. Ventanas en el **Samsung**: navegador a la izquierda, terminal con Claude a la derecha, zoom ⌘+ en ambas.
4. En el **MacBook**: este guion.
5. OBS → **Iniciar grabación** → ⌃⌥0 (Inicio) mientras arrancas, luego ⌃⌥1 (Código). Mira que el **REC esté en rojo**.

---

# PARTE PRÁCTICA

## Arranque

### Paso 1 · Presentación (~1 min)
🎙 Di:
> Hola, soy Juan Felipe Rodríguez, de la Maestría en Ciencias de la Información y las Comunicaciones de la Universidad Distrital. Hoy voy a desarrollar el Taller 5 de Inteligencia Computacional Aplicada: lógica difusa, con el cuaderno corregido que publicó el profesor.
>
> Igual que en el Taller 1, a la derecha tengo a Claude: me preparó esta guía de pasos y me propone el código de cada TODO; yo lo escribo, lo ejecuto y explico qué hace. Todo queda grabado y lo declaro en el informe.

✅ ⌘⇧→

### Paso 2 · Leer el enunciado (~2 min)
Abre `bibliografia/propuesto/Taller6B_LogicaDifusa_Propuesto_Colab.ipynb` en el navegador o en VS Code para mostrarlo.

🎙 Di:
> El cuaderno construye un **clasificador difuso con reglas sacadas de los datos**, con el método de Wang-Mendel simplificado, sobre el dataset **Wine**: 178 vinos, 13 características químicas y 3 clases. Hay seis TODO: elegir 4 características sin fuga de información, programar una función de pertenencia sigmoidal, calcular la fuerza de las reglas con dos t-normas, evaluar con matriz de confusión, comparar 2, 3 y 4 etiquetas contra un árbol de decisión, y agrupar con Fuzzy C-Means.
>
> El taller también trae una parte en MATLAB, el `.mlx`. No tengo MATLAB, así que hago la parte de Python y lo declaro en el informe; el último TODO deja los CSV listos para MATLAB.

✅ ⌘⇧→

---

## Entorno

Abre una **pestaña nueva** en la terminal (⌘T).

### Paso 3 · Copiar el cuaderno y commit inicial
⌨️ Escribe:
```bash
cd ~/repos/ud/maestria/mcic/semestre-2/mcic-computational-intelligence/2.Talleres/5.Taller
cp bibliografia/propuesto/Taller6B_LogicaDifusa_Propuesto_Colab.ipynb taller5_logica_difusa.ipynb
git add taller5_logica_difusa.ipynb
git commit -m "taller 5: cuaderno propuesto sin resolver"
```
🎙 Di:
> Copio el cuaderno del profe con mi nombre de archivo y hago un commit antes de tocarlo, para que el historial muestre qué venía del profe y qué hice yo.

✅ ⌘⇧→

### Paso 4 · Entorno con uv
⌨️ Escribe:
```bash
uv venv --python 3.12
source .venv/bin/activate
```
👀 Debe salir `Creating virtual environment at: .venv` y el prompt con `(5.Taller)` o `(.venv)`.

✅ ⌘⇧→

### Paso 5 · Instalar librerías
⌨️ Escribe:
```bash
uv pip install numpy matplotlib scikit-learn scikit-fuzzy networkx jupyterlab
uv pip freeze > requirements.txt
```
🎙 Di:
> scikit-fuzzy es la librería de lógica difusa de Python; el cuaderno la usa solo para comparar con nuestro propio código. networkx la necesita scikit-fuzzy por dentro: sin ella falla el import.

✅ ⌘⇧→

### Paso 6 · Abrir Jupyter
⌨️ Escribe:
```bash
jupyter lab
```
Abre `taller5_logica_difusa.ipynb`. Arriba de todo, inserta una celda **Markdown** (tecla `A` estando en la primera celda, luego `M`) con:
```markdown
**Estudiante:** Juan Felipe Rodríguez Galindo · 20261595004 — Taller 5 (lógica difusa), parte Python
```

✅ ⌘⇧→

---

## Paso 0 del cuaderno (código del profe)

### Paso 7 · Preparación del entorno
▶️ Ejecuta la celda `Preparación del entorno`.

👀 Debe salir: `NumPy 2.x | scikit-fuzzy 0.5.0`

🎙 Di:
> Fija la semilla 42 para que todo sea reproducible y define `verificar`, que es la función de los puntos de control.

✅ ⌘⇧→

### Paso 8 · Funciones de pertenencia y Fuzzy C-Means
▶️ Ejecuta las celdas `Funciones de pertenencia` y `Fuzzy C-Means propio`.

🎙 Di (señala cada función):
> `trimf`, `trapmf` y `gaussmf` son las funciones de pertenencia triangular, trapezoidal y gaussiana, con los mismos parámetros que en MATLAB. Devuelven un grado entre 0 y 1: qué tanto pertenece x a un conjunto.
>
> `fcm_propio` es Fuzzy C-Means: como k-medias, pero cada punto pertenece a todos los grupos con un grado, y esos grados suman 1. Alterna dos pasos: calcula los centros como promedio ponderado por los grados elevados a m, y recalcula los grados según la distancia a cada centro. m = 2 controla qué tan borrosa es la partición.

✅ ⌘⇧→

### Paso 9 · El clasificador con reglas de los datos
▶️ Ejecuta la celda `Clasificador difuso con reglas extraídas de los datos`.

🎙 Di:
> Esta es la idea central del taller. Primero normalizo cada característica a [0, 1]. Luego pongo n triángulos uniformes, por ejemplo bajo, medio y alto. Para cada muestra de entrenamiento miro en qué etiqueta tiene mayor grado cada característica: eso forma el antecedente de una regla, y la clase de la muestra es el consecuente. Si dos muestras dan el mismo antecedente, me quedo con la de mayor grado. Para predecir, calculo qué tan fuerte se dispara cada regla y gana la más fuerte.

✅ ⌘⇧→

### Paso 10 · Cargar Wine
▶️ Ejecuta las dos celdas de datos.

👀 Debe salir:
```
wine | entrenamiento: (124, 13) | prueba: (54, 13) | clases: ['class_0', 'class_1', 'class_2']
```
🎙 Di:
> 70 % para entrenar y 30 % para probar, estratificado: cada clase queda en la misma proporción en los dos conjuntos.

✅ ⌘⇧→

---

## TODO 1 a 4

### Paso 11 · TODO 1: elegir 4 características
⌨️ En la celda del TODO 1, reemplaza la línea `idx = None ...` por:
```python
selector = SelectKBest(f_classif, k=4).fit(d["Xtr"], d["ytr"])
idx = selector.get_support(indices=True)
```
▶️ Ejecuta esa celda y el **punto de control 1**.

👀 Debe salir:
```
Características elegidas: ['alcohol', 'flavanoids', 'od280/od315_of_diluted_wines', 'proline']
[OK]      idx tiene 4 índices distintos
[OK]      Coincide con los 4 mayores F calculados solo con entrenamiento
```
🎙 Di (responde la pregunta del cuaderno):
> El estadístico F del ANOVA mide qué tanto separa cada característica a las clases. Lo ajusto **solo con entrenamiento**: si usara todos los datos, la elección ya habría visto las muestras de prueba, y la exactitud que mida después sería optimista. Eso es fuga de información.

▶️ Ejecuta la celda siguiente (normaliza): `Datos normalizados: (124, 4) (54, 4)`.
🎙 Di:
> Normalizo con el mínimo y el máximo de entrenamiento, por la misma razón.

✅ ⌘⇧→

### Paso 12 · TODO 2: función sigmoidal
⌨️ En la celda `def sigmf`, reemplaza `return None` por:
```python
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + np.exp(-a * (x - c)))
```
▶️ Ejecuta la celda y el **punto de control 2**.

👀 Debe salir tres veces `[OK]`.

🎙 Di:
> Es la fórmula del enunciado. En x = c el exponente es cero y da 1/2, que es el punto de cruce. Con a positiva crece de 0 a 1; con a negativa decrece. Ojo: scikit-fuzzy recibe los parámetros al revés, primero c y luego a, por eso el punto de control llama `fuzz.sigmf(xs, 1.0, 2.0)`.

✅ ⌘⇧→

### Paso 13 · TODO 3: fuerza de las reglas
▶️ Primero ejecuta la celda tal como está para ver: `Reglas extraídas: 31`.

⌨️ En `fuerza_reglas`, reemplaza `return None` por:
```python
    if tnorma == "producto":
        return g.prod(axis=2)
    return g.min(axis=2)
```
▶️ Ejecuta la celda y el **punto de control 3**.

👀 Debe salir:
```
[OK]      Forma N x n_reglas
[OK]      Producto coincide con el cálculo manual de la primera muestra
[OK]      min >= producto (siempre, con grados en [0,1])
Exactitud en prueba con t-norma producto: 0.926
Exactitud en prueba con t-norma min: 0.926
```
🎙 Di:
> `g` tiene, para cada muestra y cada regla, el grado de cada una de las 4 condiciones. La t-norma es el "Y" difuso: con el mínimo, la regla vale lo que su condición más débil; con el producto, se multiplican. Como los grados están entre 0 y 1, multiplicar nunca da más que el mínimo. Aquí las dos dan 92.6 %: cambian los valores de fuerza, pero casi nunca cambia cuál regla gana.

✅ ⌘⇧→

### Paso 14 · TODO 4: evaluación y par más confundido
⌨️ En la celda del TODO 4, reemplaza `pred = None; exactitud = None; cm = None; par = None` por:
```python
pred = clases_r[f.argmax(axis=1)]
pred = np.where(f.max(axis=1) > 0, pred, 0)       # si ninguna regla se dispara: clase 0
exactitud = accuracy_score(d["yte"], pred)
cm = confusion_matrix(d["yte"], pred)
fuera = cm.copy()
np.fill_diagonal(fuera, 0)                         # solo los errores
par = tuple(int(v) for v in np.unravel_index(fuera.argmax(), fuera.shape))
reglas_en_palabras(R, clases_r, grados_r, car, d["clases"], N_MF, max_reglas=3)
```
▶️ Ejecuta la celda y el **punto de control 4**.

👀 Debe salir:
```
SI alcohol es medio Y flavanoids es medio Y od280/... es medio Y proline es medio ENTONCES clase = class_1   (grado 0.60)
... (dos reglas más)
Exactitud: 0.9259...
[[17  1  0]
 [ 1 18  2]
 [ 0  0 15]]
Par más confundido (real, predicha): (1, 2)
[OK] ... (tres veces)
```
🎙 Di:
> La predicción es la clase de la regla más fuerte. En la matriz, las filas son la clase real y las columnas la predicha: la diagonal son aciertos. Para el par más confundido pongo la diagonal en cero y busco el máximo: dos vinos de clase 1 se clasificaron como clase 2. Y las reglas se leen en lenguaje natural: "si alcohol es medio y flavonoides es medio... entonces clase 1". Esa es la ventaja de un sistema difuso: se puede leer.

✅ ⌘⇧→

### Paso 15 · Commit de TODO 1 a 4
⌨️ En la terminal:
```bash
git add taller5_logica_difusa.ipynb requirements.txt
git commit -m "taller 5: TODO 1 a 4 (selección, sigmf, t-normas, evaluación)"
```
✅ ⌘⇧→

---

## TODO 5 y 6

### Paso 16 · TODO 5: escribe tu predicción ANTES de ejecutar
El cuaderno lo pide. Encima de la celda del TODO 5, inserta una celda **Markdown** y escribe **con tus palabras** qué crees que va a pasar. Ideas para guiarte (no las copies, responde tú):
- ¿Más etiquetas = más reglas? ¿cuántas como máximo con 4 características? (n⁴: 16, 81, 256)
- ¿Más etiquetas = mejor exactitud siempre, o puede empeorar?
- ¿El árbol de decisión con las mismas hojas le gana al difuso o no?

🎙 Di lo mismo que escribes, en voz alta.

✅ ⌘⇧→

### Paso 17 · TODO 5: experimento
⌨️ En la celda del TODO 5, reemplaza `pass` por:
```python
    Rn, cn, gn = extraer_reglas(Xtr, d["ytr"], n)
    p, _ = predecir_reglas(Xte, Rn, cn, n)
    arbol = DecisionTreeClassifier(max_leaf_nodes=len(Rn), random_state=SEMILLA).fit(Xtr_s, d["ytr"])
    resultados.append((n, len(Rn), accuracy_score(d["yte"], p), accuracy_score(d["yte"], arbol.predict(Xte_s))))
```
▶️ Ejecuta la celda y el **punto de control 5**.

👀 Debe salir:
```
 n_mf  reglas   difusa    árbol
    2      10    0.759    0.870
    3      31    0.926    0.870
    4      43    0.889    0.870
```
y tres `[OK]`.

🎙 Di:
> Con 2 etiquetas hay solo 10 reglas y el sistema es demasiado grueso: 75.9 %. Con 3 sube a 92.6 % y le gana al árbol. Con 4 hay 43 reglas pero baja a 88.9 %: cada regla cubre menos muestras, hay más combinaciones que en prueba no tienen regla parecida, y empieza a sobreajustar. Y el número de reglas queda muy por debajo de n⁴ (16, 81, 256), porque solo aparecen las combinaciones que existen en los datos.
>
> El árbol sale igual en los tres casos. Le permito 10, 31 o 43 hojas, pero con 13 ya separa todo el entrenamiento, así que no crece más.

✅ ⌘⇧→

### Paso 18 · Figura para el informe
Inserta una celda de código **debajo** de la tabla del TODO 5:
```python
import os
ns = [r[0] for r in resultados]
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(ns, [r[2] for r in resultados], marker="o", label="Clasificador difuso")
ax.plot(ns, [r[3] for r in resultados], marker="s", label="Árbol con las mismas hojas")
for n, nr, a1, _ in resultados:
    ax.annotate(f"{nr} reglas", (n, a1), textcoords="offset points", xytext=(0, 8), ha="center")
ax.set(xlabel="Etiquetas por característica (n_mf)", ylabel="Exactitud en prueba", xticks=ns, ylim=(0.6, 1.0))
ax.legend()
os.makedirs("figuras", exist_ok=True)
plt.savefig("figuras/exactitud_nmf.png", dpi=150, bbox_inches="tight")
plt.show()
```
👀 Una gráfica: la línea difusa sube en 3 y baja en 4; la del árbol queda plana en 0.87.

✅ ⌘⇧→

### Paso 19 · TODO 5: tus 5 líneas
En la celda **"Redacte aquí (5 líneas)"**, responde **con tus palabras** las 5 preguntas. Los datos que tienes:
1. ¿Qué n_mf? → 3 (92.6 %, 31 reglas).
2. ¿Cómo cambian las reglas? → 10, 31, 43; muy lejos de n⁴ = 16, 81, 256.
3. ¿El árbol? → 87.0 % fijo; el difuso con 3 etiquetas le gana por 3 muestras.
4. ¿Interpretabilidad? → 31 reglas leíbles en palabras ("si alcohol es medio..."), frente a un árbol de 13 hojas con umbrales numéricos.
5. ¿Fiabilidad? → la prueba tiene 54 vinos: **una muestra vale 1.85 puntos**. 92.6 contra 88.9 son 2 vinos; con otra partición podría cambiar el orden.

Compara con lo que predijiste en el paso 16: ¿acertaste?

✅ ⌘⇧→

### Paso 20 · TODO 6: Fuzzy C-Means y ARI
⌨️ En la celda del TODO 6, reemplaza `ari = None` por:
```python
grupo = U.argmax(axis=0)                  # grupo de mayor pertenencia de cada muestra
ari = adjusted_rand_score(y_all, grupo)
```
▶️ Ejecuta la celda y el **punto de control 6**.

👀 Debe salir `ARI FCM: 0.794...`, dos `[OK]` y `Archivos creados: ['wine_4car_train.csv', 'wine_4car_test.csv']` (más el mensaje de "Fuera de Colab", que es normal).

🎙 Di:
> Aquí no uso las etiquetas: FCM agrupa los 178 vinos solo por sus 4 características. Después comparo los grupos con las clases reales con el ARI, que vale 0 si el agrupamiento es al azar y 1 si coincide perfecto, sin importar cómo se numeren los grupos. 0.79 dice que las tres clases de vino forman grupos naturales en estas cuatro características. Los CSV son los que usaría la parte de MATLAB.

✅ ⌘⇧→

### Paso 21 · Commit de TODO 5 y 6
⌨️ En la terminal:
```bash
git add taller5_logica_difusa.ipynb figuras wine_4car_train.csv wine_4car_test.csv
git commit -m "taller 5: TODO 5 y 6 (etiquetas vs árbol, FCM), figura y CSV"
```
✅ ⌘⇧→

---

## Cierre

### Paso 22 · Conclusiones y declaración de IA en el cuaderno
Al final del cuaderno, una celda **Markdown**. Las conclusiones **con tus palabras**, una línea por hallazgo:
1. Selección sin fuga: alcohol, flavonoides, OD280/OD315 y prolina.
2. Wang-Mendel con 3 etiquetas: 31 reglas y 92.6 % en prueba; mínimo y producto dan lo mismo aquí.
3. El error principal: clase 1 → clase 2 (2 vinos).
4. Más etiquetas no siempre es mejor: 75.9 / 92.6 / 88.9 %; el árbol, 87.0 %.
5. FCM sin etiquetas: ARI 0.79.

Y la declaración. Esta es la que corresponde a cómo lo hiciste (el profe pide herramienta, partes y verificación):
```markdown
## Declaración de uso de IA
Usé Claude (Anthropic). Preparó la guía de pasos y propuso el código de los TODO; yo lo escribí, lo ejecuté y expliqué cada parte en el video, y verifiqué los resultados con los puntos de control del cuaderno. La predicción y las conclusiones las redacté yo. La parte en MATLAB no se desarrolló porque no tengo MATLAB; el cuaderno deja exportados los CSV para hacerla.
```
✅ ⌘⇧→

### Paso 23 · Cierre del video (~1 min)
🎙 Di:
> Eso es todo el Taller 5: los seis TODO resueltos con sus puntos de control en verde, la comparación de etiquetas contra el árbol y el agrupamiento con Fuzzy C-Means. El informe lo hago aparte con estos resultados. Gracias.

⌨️ Último commit:
```bash
git add taller5_logica_difusa.ipynb
git commit -m "taller 5: conclusiones y declaración de IA"
```
✅ ⌘⇧→ → OBS **Detener grabación**.

---

# PARTE DEL INFORME (sin grabar)

Va en `2.Talleres/5.Taller/informe/` con la plantilla UD, como el Taller 1. Corto: 4 a 6 páginas. **Nada de extras** (el profe castigó la validación cruzada, ridge, 20 particiones…), nada de archivos que no se entregan, y rotulado **Taller 5**.

1. **Introducción** (1 párrafo): clasificador difuso con reglas extraídas de datos sobre Wine; solo la parte Python, y por qué.
2. **Marco teórico** (corto): funciones de pertenencia (triangular y sigmoidal), t-normas mínimo y producto, Wang-Mendel simplificado, FCM y ARI.
3. **Metodología**: partición 70/30 estratificada con semilla 42, SelectKBest solo con entrenamiento, normalización con el rango de entrenamiento, n_mf = 2, 3, 4, árbol con `max_leaf_nodes` = número de reglas, FCM con c = 3 y m = 2.
4. **Resultados**:
   - Tabla 1: características elegidas.
   - Tabla 2: t-norma producto contra mínimo (31 reglas, 92.6 % las dos).
   - Tabla 3: matriz de confusión y las 3 reglas en palabras.
   - Tabla 4 y Figura 1: n_mf contra reglas, exactitud difusa y árbol (`figuras/exactitud_nmf.png`).
   - ARI = 0.79.
   Cada tabla y figura citada en el texto.
5. **Análisis**: por qué 3 etiquetas es el punto medio (pocas = grueso, muchas = reglas sin soporte); por qué las reglas son muchas menos que n⁴; por qué el árbol no cambia (13 hojas puras); por qué min y producto coinciden; tamaño de la prueba (1 vino = 1.85 puntos); qué significa el ARI.
6. **Conclusiones**: las 5 del paso 22.
7. **Declaración de uso de IA**: la del paso 22, más el enlace al video y que el informe se redactó con ayuda de Claude si es así.

### Entrega (`2.Talleres/5.Taller/entrega/`)
- `juan-rodriguez-20261595004-taller-5.pdf` (informe)
- `juan-rodriguez-20261595004-taller-5.ipynb` (cuaderno ejecutado)
- `requirements.txt`
- `wine_4car_train.csv`, `wine_4car_test.csv` (los genera el cuaderno)
- Enlace al video (YouTube, no listado)
